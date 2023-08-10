import moderngl
from PIL import Image
from shapefile_utils import load_shapefile, calculate_scaling
from render_utils import create_shader_program, render_coords
from shapely.ops import unary_union

from constants import IMAGE_WIDTH, IMAGE_HEIGHT


def main():
    # Initialize ModernGL context
    context = moderngl.create_standalone_context()

    # Load the shapefile
    shapes = load_shapefile("../data/okcounties.shp")
    state_boundary = unary_union(shapes)

    # Calculate scaling and bounds
    scale, min_lon, min_lat = calculate_scaling(shapes)

    # Framebuffers initialization
    samples = 4
    multisample_texture = context.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4, samples=samples)
    multisample_framebuffer = context.framebuffer(color_attachments=[multisample_texture])
    main_framebuffer = context.framebuffer(color_attachments=[context.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4)])

    multisample_framebuffer.use()
    context.clear(1.0, 1.0, 1.0, 1.0)

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

    # Render counties and boundaries
    for shp in shapes:
        if shp.geom_type == 'MultiPolygon':
            for polygon in shp.geoms:
                render_coords(context, polygon.exterior.coords, shader_grey, scale, min_lon, min_lat)
        else:
            render_coords(context, shp.exterior.coords, shader_grey, scale, min_lon, min_lat)

    if state_boundary.geom_type == 'MultiPolygon':
        for polygon in state_boundary.geoms:
            render_coords(context, polygon.exterior.coords, shader_black, scale, min_lon, min_lat)
    else:
        render_coords(context, state_boundary.exterior.coords, shader_black, scale, min_lon, min_lat)

    # Resolve multisample framebuffer to standard framebuffer
    context.copy_framebuffer(dst=main_framebuffer, src=multisample_framebuffer)

    # Save the result
    pixels = main_framebuffer.read(components=4)
    image = Image.frombytes('RGBA', main_framebuffer.size, pixels).transpose(Image.FLIP_TOP_BOTTOM)
    image.save('../data/output.png')


if __name__ == "__main__":
    main()
