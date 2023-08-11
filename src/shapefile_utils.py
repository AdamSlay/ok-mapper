import shapefile
from shapely.geometry import shape as shapely_shape

from constants import DRAW_WIDTH, DRAW_HEIGHT


def load_shapefile(file_path):
    """Loads and processes the shapefile."""
    sf = shapefile.Reader(file_path)
    return [shapely_shape(shp.__geo_interface__) for shp in sf.shapes()]


def calculate_scaling(shapes):
    """Computes the scaling factors based on provided shapes."""

    all_points = collect_all_points(shapes)

    # find the min and max values for x and y through all points
    min_lon = min([x for x, y in all_points])
    max_lon = max([x for x, y in all_points])
    min_lat = min([y for x, y in all_points])
    max_lat = max([y for x, y in all_points])

    # calculate the scaling factor for xax and yax based on the drawing area and the min/max coords
    scale_x = DRAW_WIDTH / (max_lon - min_lon)
    scale_y = DRAW_HEIGHT / (max_lat - min_lat)

    # find the smaller scaling factor to make the map fit inside the drawing area without being distorted
    final_scale = min(scale_x, scale_y)

    # scale the map down a bit to make sure it fits inside the drawing area without being cut off
    final_scale *= 0.95

    return final_scale, min_lon, min_lat


def collect_all_points(shapes):
    """Collect all points from the shapes."""
    all_points = []

    for shp in shapes:
        if shp.geom_type == 'MultiPolygon':
            # If the shape is a polygon within a polygon like an island or similar, we need to iterate over each polygon
            for polygon in shp.geoms:
                all_points.extend(polygon.exterior.coords)
        else:
            all_points.extend(shp.exterior.coords)
    return all_points
