import moderngl
from PIL import Image
from shapely.ops import unary_union

from constants import IMAGE_WIDTH, IMAGE_HEIGHT
from render_utils import render_all_shapes
from shapefile_utils import load_shapefile


def main():
    # Initialize ModernGL context
    context = moderngl.create_standalone_context()

    # Load the shapefile
    shapes = load_shapefile("../data/okcounties.shp")

    # Create a single polygon from all exterior boundaries thus creating a border around the state
    state_boundary = unary_union(shapes)

    # Framebuffers initialization
    samples = 4
    multisample_texture = context.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4, samples=samples)
    multisample_framebuffer = context.framebuffer(color_attachments=[multisample_texture])
    main_framebuffer = context.framebuffer(color_attachments=[context.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4)])

    multisample_framebuffer.use()
    context.clear(1.0, 1.0, 1.0, 1.0)

    render_all_shapes(context, shapes, state_boundary)

    # Resolve multisample framebuffer to standard framebuffer
    context.copy_framebuffer(dst=main_framebuffer, src=multisample_framebuffer)

    # Save the result
    pixels = main_framebuffer.read(components=4)
    image = Image.frombytes('RGBA', main_framebuffer.size, pixels).transpose(Image.FLIP_TOP_BOTTOM)
    image.save('../data/output.png')


if __name__ == "__main__":
    main()
