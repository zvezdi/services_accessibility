from typing import Tuple, Union
from pyproj import Transformer
from shapely.geometry import Point, MultiPoint, LineString, Polygon, MultiPolygon, GeometryCollection

BGS2005 = "EPSG:7801"
WGS84 = "EPSG:4326"

def get_transformer(source_crs: str = BGS2005, target_crs: str = WGS84, always_xy: bool = True):
    return Transformer.from_crs(source_crs, target_crs, always_xy)

def crs_transform_point(transformer: Transformer, point: Point, swap_coords: bool = False) -> Point:
    """ In the database we have point in 7801 (x, y) which translates to 4326 (lon, lat),
    however plotting libraries use 4326 (lat, lon)
    """
    lon, lat = transformer.transform(point.x, point.y)
    return Point(lat, lon) if swap_coords else Point(lon, lat)

def crs_transform_multipoint(transformer: Transformer, multipoint: MultiPoint, swap_coords: bool = False) -> MultiPoint:
    if not multipoint.is_valid:
        raise ValueError("Not Valid")
    transformed_points = [
        crs_transform_point(transformer, point, swap_coords) for point in multipoint.geoms
    ]
    return MultiPoint(transformed_points)

def crs_transform_coords(transformer: Transformer, x: float, y: float, swap_coords: bool = False, toPoint: bool = False) -> Union[Tuple[float, float], Point]:
    """ In the database we have point in 7801 (x, y) which translates to 4326 (lon, lat),
    however plotting libraries use 4326 (lat, lon)
    """
    lon, lat = transformer.transform(x, y)

    if swap_coords:
        return Point(lat, lon) if toPoint else (lat, lon)
    
    return Point(lon, lat) if toPoint else (lon, lat)

def crs_transform_linestring(transformer: Transformer, linestring: LineString, swap_coords: bool = False) -> LineString:
    """ In the database we have point in 7801 (x, y) which translates to 4326 (lon, lat),
    however plotting libraries use 4326 (lat, lon)
    """
    transformed_coords = [transformer.transform(x, y) for x, y in linestring.coords]

    if swap_coords:
        transformed_coords = [(lat, lon) for lon, lat in transformed_coords]

    return LineString(transformed_coords)

def crs_transform_polygon(transformer: Transformer, polygon: Polygon, swap_coords: bool = False) -> Polygon:
    """ In the database we have point in 7801 (x, y) which translates to 4326 (lon, lat),
    however plotting libraries use 4326 (lat, lon)
    """
    if not polygon.is_valid:
        raise ValueError("Not Valid")
    transformed_coords = [transformer.transform(x, y) for x, y in polygon.exterior.coords]

    if swap_coords:
        transformed_coords = [(lat, lon) for lon, lat in transformed_coords]

    return Polygon(transformed_coords)

def crs_transform_multipolygon(transformer: Transformer, multipolygon: MultiPolygon, swap_coords: bool = False) -> MultiPolygon:
    if not multipolygon.is_valid:
        raise ValueError("Not Valid")
    transformed_polygons = [
        crs_transform_polygon(transformer, polygon, swap_coords) for polygon in multipolygon.geoms
    ]
    return MultiPolygon(transformed_polygons)

def crs_transform_geometrycollection(transformer, geometry_collection: GeometryCollection, swap_coords: bool = False) -> GeometryCollection:
    transformed_geometries = []
    for geom in geometry_collection.geoms:
        transformed_geom = crs_transform(transformer, geom, swap_coords)
        transformed_geometries.append(transformed_geom)
    return GeometryCollection(transformed_geometries)

def crs_transform(transformer: Transformer, shapely_object: Union[Point, MultiPoint, LineString, Polygon, MultiPolygon, GeometryCollection], 
                  swap_coords: bool = False) -> Union[Point, MultiPoint, LineString, Polygon, MultiPolygon, GeometryCollection]:
    if shapely_object.geom_type == 'Point':
        return crs_transform_point(transformer, shapely_object, swap_coords)
    elif shapely_object.geom_type == 'MultiPoint':
        return crs_transform_multipoint(transformer, shapely_object, swap_coords)
    elif shapely_object.geom_type == 'LineString':
        return crs_transform_linestring(transformer, shapely_object, swap_coords)
    elif shapely_object.geom_type == 'Polygon':
        return crs_transform_polygon(transformer, shapely_object, swap_coords)
    elif shapely_object.geom_type == 'MultiPolygon':
        return crs_transform_multipolygon(transformer, shapely_object, swap_coords)
    elif shapely_object.geom_type == 'GeometryCollection':
        return crs_transform_geometrycollection(transformer, shapely_object, swap_coords)
    else:
        raise ValueError(f"Don't know how to crs transform a {shapely_object.geom_type}")
