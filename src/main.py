import moderngl
import shapefile
import struct
from PIL import Image
from shapely.geometry import shape as shapely_shape
from shapely.ops import unary_union

# Constants
# Image settings
IMAGE_WIDTH = 770
IMAGE_HEIGHT = 420
MARGIN = 50
DRAW_WIDTH = IMAGE_WIDTH - 2 * MARGIN
DRAW_HEIGHT = IMAGE_HEIGHT - 2 * MARGIN

# Geographical transformations
VERT_STRETCH = 1.08
XAX_SHIFT = 0.08
YAX_SHIFT = 0.05

# Initialize ModernGL context
ctx = moderngl.create_standalone_context()


def load_shapefile(file_path):
    """Loads and processes the shapefile."""
    sf = shapefile.Reader(file_path)
    return [shapely_shape(shp.__geo_interface__) for shp in sf.shapes()]


def calculate_scaling(points):
    """Computes the scaling factors based on provided points."""
    min_lon = min([x for x, y in points])
    max_lon = max([x for x, y in points])
    min_lat = min([y for x, y in points])
    max_lat = max([y for x, y in points])
    scale_x = DRAW_WIDTH / (max_lon - min_lon)
    scale_y = DRAW_HEIGHT / (max_lat - min_lat)
    return min(scale_x, scale_y) * 0.95, min_lon, min_lat


def create_shader_program(vertex_shader, fragment_shader):
    """Creates and returns a shader program."""
    return ctx.program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader
    )


def render_coords(coords, program, scale, min_lon, min_lat):
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


def main():
    # Load the shapefile
    shapes = load_shapefile("../data/okcounties.shp")
    state_boundary = unary_union(shapes)

    # Collect all points from the shapes
    all_points = []
    for shp in shapes:
        if shp.geom_type == 'MultiPolygon':
            for polygon in shp.geoms:
                all_points.extend(polygon.exterior.coords)
        else:
            all_points.extend(shp.exterior.coords)

    # Calculate scaling and bounds
    scale, min_lon, min_lat = calculate_scaling(all_points)

    # Framebuffers initialization
    samples = 4
    ms_texture = ctx.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4, samples=samples)
    ms_fbo = ctx.framebuffer(color_attachments=[ms_texture])
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((IMAGE_WIDTH, IMAGE_HEIGHT), 4)])

    ms_fbo.use()
    ctx.clear(1.0, 1.0, 1.0, 1.0)

    # Shader programs
    prog_grey = create_shader_program(
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
                render_coords(polygon.exterior.coords, prog_grey, scale, min_lon, min_lat)
        else:
            render_coords(shp.exterior.coords, prog_grey, scale, min_lon, min_lat)

    if state_boundary.geom_type == 'MultiPolygon':
        for polygon in state_boundary.geoms:
            render_coords(polygon.exterior.coords, prog_black, scale, min_lon, min_lat)
    else:
        render_coords(state_boundary.exterior.coords, prog_black, scale, min_lon, min_lat)

    # Resolve multisample framebuffer to standard framebuffer
    ctx.copy_framebuffer(dst=fbo, src=ms_fbo)

    # Save the result
    pixels = fbo.read(components=4)
    image = Image.frombytes('RGBA', fbo.size, pixels).transpose(Image.FLIP_TOP_BOTTOM)
    image.save('../data/output.png')


if __name__ == "__main__":
    main()
