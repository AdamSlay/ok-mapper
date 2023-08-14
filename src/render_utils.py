import moderngl
import numpy as np
import struct

from constants import IMAGE_WIDTH, IMAGE_HEIGHT, DRAW_WIDTH, DRAW_HEIGHT, MARGIN, VERT_STRETCH, XAX_SHIFT, YAX_SHIFT
from shaders import *
from shapefile_utils import calculate_scaling


def render_all_shapes(context, counties, border):
    # Shader programs
    shader_grey = context.program(vertex_shader=VERTEX_OUTLINE_GREY, fragment_shader=FRAGMENT_OUTLINE_GREY)
    shader_black = context.program(vertex_shader=VERTEX_OUTLINE_BLACK, fragment_shader=FRAGMENT_OUTLINE_BLACK)

    # Calculate scaling and bounds
    scale_factor, min_lon, min_lat = calculate_scaling(counties)

    # Render counties and boundary
    for shp in counties:
        if shp.geom_type == 'MultiPolygon':
            for polygon in shp.geoms:
                render_coords(context, polygon.exterior.coords, shader_grey, scale_factor, min_lon, min_lat)
        else:
            render_coords(context, shp.exterior.coords, shader_grey, scale_factor, min_lon, min_lat)

    for shp in border:
        if shp.geom_type == 'MultiPolygon':
            for polygon in shp.geoms:
                render_coords(context, polygon.exterior.coords, shader_black, scale_factor, min_lon, min_lat)
        else:
            render_coords(context, shp.exterior.coords, shader_black, scale_factor, min_lon, min_lat)
    return


def create_shader_program(context, vertex_shader, fragment_shader):
    """Creates and returns a shader program."""
    return context.program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader
    )


def render_coords(context, coords, program, scale, min_lon, min_lat):
    """Function to render coordinates with a given shader program."""
    transformed_vertices = [
        (
            (2 * (x - min_lon) * scale / DRAW_WIDTH - 1 + 2 * MARGIN / IMAGE_WIDTH) - XAX_SHIFT,
            2 * (y - min_lat) * (scale * VERT_STRETCH) / DRAW_HEIGHT - 1 + 2 * MARGIN / IMAGE_HEIGHT - YAX_SHIFT
        )
        for x, y in coords
    ]
    vertex_data = []
    for x, y in transformed_vertices:
        vertex_data.extend(struct.pack('2f', x, y))
    vertex_buffer = context.buffer(data=bytearray(vertex_data))
    vao = context.simple_vertex_array(program, vertex_buffer, 'in_vert')
    vao.render(moderngl.LINE_STRIP)


def transform_coordinates(lon, lat, scale_factor, min_lon, min_lat):
    transformed_lon = (2 * (lon - min_lon) * scale_factor / DRAW_WIDTH - 1 + 2 * MARGIN / IMAGE_WIDTH) - XAX_SHIFT
    transformed_lat = 2 * (lat - min_lat) * (
            scale_factor * VERT_STRETCH) / DRAW_HEIGHT - 1 + 2 * MARGIN / IMAGE_HEIGHT - YAX_SHIFT
    return transformed_lon, transformed_lat


def create_circle_vertex_data(cx, cy, r, segments):
    # The center of the circle
    vertices = [cx, cy]
    aspect_ratio = 770.0 / 420.0

    # Calculate the vertices for the segments
    for i in range(segments + 1):
        theta = 2.0 * 3.1415926 * float(i) / float(segments)
        dx = r * np.cos(theta)
        dy = r * np.sin(theta) * aspect_ratio
        vertices.extend([cx + dx, cy + dy])

    return vertices


def render_points(context, data, counties):
    # Create the shaders
    shader = context.program(vertex_shader=VERTEX_POINT_GREY, fragment_shader=FRAGMENT_POINT_GREY)

    # Calculate scaling and bounds
    scale_factor, min_lon, min_lat = calculate_scaling(counties)

    for station in data:
        lon = station['lon']
        lat = station['lat']
        transformed_lon, transformed_lat = transform_coordinates(lon, lat, scale_factor, min_lon, min_lat)

        # Assuming you want a radius of 0.05 (you can adjust this)
        circle_data = create_circle_vertex_data(transformed_lon, transformed_lat, 0.005, 32)

        # Send data to GPU
        vbo = context.buffer(np.array(circle_data, dtype='f4').tobytes())
        vao = context.simple_vertex_array(shader, vbo, 'in_vert')

        # Render as triangle fan
        vao.render(moderngl.TRIANGLE_FAN)
