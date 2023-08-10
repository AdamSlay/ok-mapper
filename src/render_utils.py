import moderngl
import struct

from constants import IMAGE_WIDTH, IMAGE_HEIGHT, DRAW_WIDTH, DRAW_HEIGHT, MARGIN, VERT_STRETCH, XAX_SHIFT, YAX_SHIFT


def create_shader_program(ctx, vertex_shader, fragment_shader):
    """Creates and returns a shader program."""
    return ctx.program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader
    )


def render_coords(ctx, coords, program, scale, min_lon, min_lat):
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
    vertex_buffer = ctx.buffer(data=bytearray(vertex_data))
    vao = ctx.simple_vertex_array(program, vertex_buffer, 'in_vert')
    vao.render(moderngl.LINE_STRIP)
