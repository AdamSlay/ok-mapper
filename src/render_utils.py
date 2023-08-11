import moderngl
import struct

from constants import IMAGE_WIDTH, IMAGE_HEIGHT, DRAW_WIDTH, DRAW_HEIGHT, MARGIN, VERT_STRETCH, XAX_SHIFT, YAX_SHIFT
from shapefile_utils import calculate_scaling


def render_all_shapes(context, shapes, state_boundary):
    # Shader programs
    shader_grey = create_shader_program(
        context,
        vertex_shader='''
            #version 330
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        ''',
        fragment_shader='''
            #version 330
            out vec4 color;
            void main() {
                color = vec4(0.6, 0.6, 0.6, 1.0);
            }
        '''
    )

    shader_black = create_shader_program(
        context,
        vertex_shader='''
            #version 330
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        ''',
        fragment_shader='''
            #version 330
            out vec4 color;
            void main() {
                color = vec4(0.0, 0.0, 0.0, 1.0);
            }
        '''
    )

    # Calculate scaling and bounds
    scale_factor, min_lon, min_lat = calculate_scaling(shapes)

    # Render counties and boundary
    for shp in shapes:
        if shp.geom_type == 'MultiPolygon':
            for polygon in shp.geoms:
                render_coords(context, polygon.exterior.coords, shader_grey, scale_factor, min_lon, min_lat)
        else:
            render_coords(context, shp.exterior.coords, shader_grey, scale_factor, min_lon, min_lat)

    for shp in state_boundary:
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
