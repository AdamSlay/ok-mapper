import moderngl
from PIL import Image
from shapefile_utils import load_shapefile, calculate_scaling
from render_utils import create_shader_program, render_coords
from shapely.ops import unary_union

from constants import IMAGE_WIDTH, IMAGE_HEIGHT


def main():
    # Initialize ModernGL context
    ctx = moderngl.create_standalone_context()

    # Load the shapefile
    shapes = load_shapefile("../data/okcounties.shp")
    state_boundary = unary_union(shapes)

    # Calculate scaling and bounds
    scale, min_lon, min_lat = calculate_scaling(shapes)

    # Framebuffers initialization
    samples = 4
    ms_texture = ctx.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4, samples=samples)
    ms_fbo = ctx.framebuffer(color_attachments=[ms_texture])
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4)])

    ms_fbo.use()
    ctx.clear(1.0, 1.0, 1.0, 1.0)

    # Shader programs
    prog_grey = create_shader_program(
        ctx,
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

    prog_black = create_shader_program(
        ctx,
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
                render_coords(ctx, polygon.exterior.coords, prog_grey, scale, min_lon, min_lat)
        else:
            render_coords(ctx, shp.exterior.coords, prog_grey, scale, min_lon, min_lat)

    if state_boundary.geom_type == 'MultiPolygon':
        for polygon in state_boundary.geoms:
            render_coords(ctx, polygon.exterior.coords, prog_black, scale, min_lon, min_lat)
    else:
        render_coords(ctx, state_boundary.exterior.coords, prog_black, scale, min_lon, min_lat)

    # Resolve multisample framebuffer to standard framebuffer
    ctx.copy_framebuffer(dst=fbo, src=ms_fbo)

    # Save the result
    pixels = fbo.read(components=4)
    image = Image.frombytes('RGBA', fbo.size, pixels).transpose(Image.FLIP_TOP_BOTTOM)
    image.save('../data/output.png')


if __name__ == "__main__":
    main()
