import numpy as np

import shapefile
from shapely.geometry import Polygon, MultiPolygon, Point

def shape2parts(shape):
    parts = []
    start_indexes = shape.parts
    prev_start_index = 0
    for start_index in start_indexes[1:]:
        parts.append(shape.points[prev_start_index:start_index])
        prev_start_index = start_index
    parts.append(shape.points[prev_start_index:])

    return parts

def shape2multi(shape):
    parts = shape2parts(shape)
    polygons = []
    for part in parts:
        polygons.append(Polygon(part))

    return MultiPolygon(polygons)

## To use, first writer as:
# writer = shapefile.Writer(shapefile.POLYGON)
# writer.autoBalance = 1
## After all are written, save it:
# writer.save('output/australia')
def write_polys(writer, polygon, attribs=None):
    if type(polygon) is Polygon:
        writer.poly(shapeType=shapefile.POLYGON, parts=[polygon.exterior.coords])
        if attribs is not None:
            writer.record(*attribs)
    else:
        writer.poly(shapeType=shapefile.POLYGON, parts=[geom.exterior.coords for geom in polygon.geoms])
        if attribs is not None:
            writer.record(*attribs)
        return
        # Delete below, if above works!
        for geom in polygon.geoms:
            writer.poly(shapeType=shapefile.POLYGON, parts=[geom.exterior.coords])
            if attribs is not None:
                writer.record(*attribs)

def gcd_slc(long0, lat0, longs, lats):
    R = 6371 # Earth mean radius [km]
    long0 = long0 * np.pi / 180
    lat0 = lat0 * np.pi / 180
    longs = longs * np.pi / 180
    lats = lats * np.pi / 180

    dists = np.arccos(np.sin(lat0)*np.sin(lats) + np.cos(lat0)*np.cos(lats) * np.cos(longs-long0)) * R
    return dists # Distance in km

def weighted_grid_within(multi, latitude, longitude, callback, shape=(1,)):
    """Determines weighted sum of the values of callback, weighted by the
hectares represented in each grid cell.  Can handle np.array returned from callback.
Returns the weighted area, and the absolute area."""
    validlon = (longitude >= multi.bounds[0]) & (longitude <= multi.bounds[2])
    validlat = (latitude >= multi.bounds[1]) & (latitude <= multi.bounds[3])

    lons_rad = longitude * np.pi / 180
    lats_rad = latitude * np.pi / 180
    dlon_rad = np.mean(np.diff(lons_rad))
    dlat_rad = np.mean(np.diff(lats_rad))

    totals = np.zeros(shape)
    for rr in np.flatnonzero(validlat):
        for cc in np.flatnonzero(validlon):
            if multi.contains(Point(longitude[cc], latitude[rr])):
                fraction = dlon_rad * abs(np.sin(lats_rad[rr] - dlat_rad / 2) - np.sin(lats_rad[rr] + dlat_rad / 2)) / (4 * np.pi) # fraction of a sphere
                area = 5.10064472e10 * fraction # hectares
                totals += area * callback(rr, cc)

    return totals
