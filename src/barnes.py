# Barnes Interpolation
from constants import *
import numpy as np


def gaussian(distance, scale_factor):
    """Compute the weight using the Gaussian function."""
    return np.exp(-distance ** 2 / (2 * scale_factor ** 2))


def barnes_interpolation(grid, stations, scale_factor, iterations=1):
    """Perform Barnes interpolation over the grid."""

    # First Guess
    for i, j in np.ndindex(grid.shape):
        lon, lat = grid_coords_to_lon_lat(i, j, SCALE_FACTOR, MIN_LON, MIN_LAT)
        weights = np.array(
            [gaussian(np.linalg.norm(np.array([lon, lat]) - np.array([station['lon'], station['lat']])), scale_factor)
             for station in stations])
        grid[i, j] = np.sum(weights * np.array([station['tair'] for station in stations])) / np.sum(weights)

    # Successive Corrections
    for iteration in range(iterations - 1):
        corrections = np.zeros_like(grid)
        for i, j in np.ndindex(grid.shape):
            lon, lat = grid_coords_to_lon_lat(i, j, SCALE_FACTOR, MIN_LON, MIN_LAT)
            differences = np.array([station['tair'] - grid[i, j] for station in stations])
            weights = np.array([gaussian(
                np.linalg.norm(np.array([lon, lat]) - np.array([station['lon'], station['lat']])), scale_factor) for
                                station in stations])
            corrections[i, j] = np.sum(weights * differences) / np.sum(weights)
        grid += corrections

    return grid


def grid_coords_to_lon_lat(i, j, scale_factor, min_lon, min_lat):
    """Convert grid coordinates (i, j) back to (lon, lat) based on transformations."""

    # Convert grid indices to adjusted OpenGL coordinates
    transformed_lon = 2 * (i / IMAGE_WIDTH) - 1
    transformed_lat = 2 * (j / IMAGE_HEIGHT) - 1

    # Adjust for margins
    transformed_lon = transformed_lon - 2 * MARGIN / IMAGE_WIDTH + XAX_SHIFT
    transformed_lat = transformed_lat - 2 * MARGIN / IMAGE_HEIGHT + YAX_SHIFT

    # Convert to normalized values (0 to 1)
    normalized_lon = (transformed_lon + 1) / 2
    normalized_lat = (transformed_lat + 1) / 2

    # Convert to scaled differences
    scaled_lon_diff = normalized_lon * DRAW_WIDTH
    scaled_lat_diff = normalized_lat * DRAW_HEIGHT

    # Obtain actual lon and lat values
    lon = scaled_lon_diff / scale_factor + min_lon
    lat = scaled_lat_diff / (scale_factor * VERT_STRETCH) + min_lat

    return lon, lat

