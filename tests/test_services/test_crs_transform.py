import pytest
from shapely.geometry import Point, MultiPoint, LineString, Polygon, MultiPolygon, GeometryCollection
from service_accessibility.services.crs_transform import (
    crs_transform, crs_transform_coords
)

def test_crs_transform_point():
    point = Point(321812.94252381043, 4731192.267176171)
    transformed = crs_transform(point, swap_coords=True)
    assert transformed.x == pytest.approx(42.696, abs=1e-3)
    assert transformed.y == pytest.approx(23.325, abs=1e-3)

    transformed = crs_transform(point, swap_coords=False)
    assert transformed.x == pytest.approx(23.325, abs=1e-3)
    assert transformed.y == pytest.approx(42.696, abs=1e-3)

def test_crs_transform_multipoint():
    multipoint = MultiPoint([(321812.94252381043, 4731192.267176171), (321813.94252381043, 4731193.267176171)])
    transformed = crs_transform(multipoint, swap_coords=True)
    assert transformed.geoms[0].x == pytest.approx(42.696, abs=1e-3)
    assert transformed.geoms[0].y == pytest.approx(23.325, abs=1e-3)

def test_crs_transform_coords():
    lon, lat = crs_transform_coords(321812.94252381043, 4731192.267176171)
    assert lon == pytest.approx(23.325, abs=1e-3)
    assert lat == pytest.approx(42.696, abs=1e-3)

    lat, lon = crs_transform_coords(321812.94252381043, 4731192.267176171, swap_coords=True)
    assert lon == pytest.approx(23.325, abs=1e-3)
    assert lat == pytest.approx(42.696, abs=1e-3)

    point = crs_transform_coords(321812.94252381043, 4731192.267176171, toPoint=True)
    assert isinstance(point, Point)
    assert point.x == pytest.approx(23.325, abs=1e-3)
    assert point.y == pytest.approx(42.696, abs=1e-3)

def test_crs_transform_linestring():
    linestring = LineString([(320960.4910, 4728848.5264), (320844.2254, 4728875.6080), (320794.2176, 4729493.6845)])
    transformed = crs_transform(linestring)
    assert transformed.coords[0][0] == pytest.approx(23.315, abs=1e-3)
    assert transformed.coords[0][1] == pytest.approx(42.674, abs=1e-3)

def test_crs_transform_polygon():
    polygon = Polygon([(320960.4910, 4728848.5264), (320844.2254, 4728875.6080), (320794.2176, 4729493.6845), (320960.4910, 4728848.5264)])
    transformed = crs_transform(polygon)
    assert transformed.exterior.coords[0][0] == pytest.approx(23.315, abs=1e-3)
    assert transformed.exterior.coords[0][1] == pytest.approx(42.674, abs=1e-3)

def test_crs_transform_multipolygon():
    multipolygon = MultiPolygon([Polygon([(320960.4910, 4728848.5264), (320844.2254, 4728875.6080), (320794.2176, 4729493.6845), (320960.4910, 4728848.5264)])])
    transformed = crs_transform(multipolygon)
    assert transformed.geoms[0].exterior.coords[0][0] == pytest.approx(23.315, abs=1e-3)
    assert transformed.geoms[0].exterior.coords[0][1] == pytest.approx(42.674, abs=1e-3)

def test_crs_transform_geometrycollection():
    point = Point(321812.94252381043, 4731192.267176171)
    linestring = LineString([(320960.4910, 4728848.5264), (320844.2254, 4728875.6080)])
    collection = GeometryCollection([point, linestring])
    transformed = crs_transform(collection)
    assert isinstance(transformed, GeometryCollection)
    assert transformed.geoms[0].x == pytest.approx(23.325, abs=1e-3)
    assert transformed.geoms[0].y == pytest.approx(42.696, abs=1e-3)
