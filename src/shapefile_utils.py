import shapefile
from shapely.geometry import shape as shapely_shape

from constants import DRAW_WIDTH, DRAW_HEIGHT


def load_shapefile(file_path):
    """Loads and processes the shapefile."""
    sf = shapefile.Reader(file_path)
    return [shapely_shape(shp.__geo_interface__) for shp in sf.shapes()]


def calculate_scaling(shapes):
    """Computes the scaling factors based on provided shapes."""

    all_points = []

    for shp in shapes:
        if shp.geom_type == 'MultiPolygon':
            for polygon in shp.geoms:
                all_points.extend(polygon.exterior.coords)
        else:
            all_points.extend(shp.exterior.coords)

    min_lon = min([x for x, y in all_points])
    max_lon = max([x for x, y in all_points])
    min_lat = min([y for x, y in all_points])
    max_lat = max([y for x, y in all_points])

    scale_x = DRAW_WIDTH / (max_lon - min_lon)
    scale_y = DRAW_HEIGHT / (max_lat - min_lat)

    return min(scale_x, scale_y) * 0.95, min_lon, min_lat


def collect_all_points(shapes):
    """Collect all points from the shapes."""
    all_points = []
    for shp in shapes:
        if shp.geom_type == 'MultiPolygon':
            for polygon in shp.geoms:
                all_points.extend(polygon.exterior.coords)
        else:
            all_points.extend(shp.exterior.coords)
    return all_points
