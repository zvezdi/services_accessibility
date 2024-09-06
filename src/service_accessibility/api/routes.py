from fastapi import APIRouter, Query
from shapely.geometry import Point, mapping

from ..services import school_service
from ..services import residential_buildings_service
from ..services import urban_planning_unit_service
from ..services.network import PedestrianGraph
from ..services.walkability_service import compute_accessibility_index

router = APIRouter()

@router.get("/pedestrian_network")
async def get_pedestrian_network():
    G = PedestrianGraph.load_graph(data_dir='data', filename='extended_network')
    return G.graph_to_geojson()

@router.get("/residential_buildings")
async def residential_buildings():
    residential_buildings = residential_buildings_service.get_all()
    return {
        "type": "FeatureCollection",
        "features": residential_buildings
    }

@router.get("/urban_planning_units")
async def get_urban_planning_units():
    urban_planning_units = urban_planning_unit_service.get_all()
    return {
        "type": "FeatureCollection",
        "features": urban_planning_units
    }

@router.get("/schools")
async def get_schools():
    schools = school_service.get_all()
    return {
        "type": "FeatureCollection",
        "features": schools
    }

@router.get("/get_closeby_amenities")
# http://localhost:8000/get_closeby_amenities?x=316221.88866994827&y=4729194.708270278&length_type=length_m&max_distance=1000
async def get_closeby_amenities(
    x: float = Query(..., description="X coordinate of the point"),
    y: float = Query(..., description="Y coordinate of the point"),
    length_type: str = Query("length_m", description="Type of distance metric"),
    max_distance: int = Query(1000, description="Maximum distance for isochrones"),
):
    G = PedestrianGraph.load_graph(data_dir='data', filename='extended_network')
    source_point = Point(x, y)
    amenities = G.get_closeby_amenities(source_point, length_type, max_distance)
    return amenities

@router.get("/get_accessibility_index")
# http://localhost:8000/get_accessibility_index?x=316221.88866994827&y=4729194.708270278&length_type=length_m&max_distance=1000&k=100&max_amenities=3&f=0.2
async def get_accessibility_index(
    x: float = Query(..., description="X coordinate of the point"),
    y: float = Query(..., description="Y coordinate of the point"),
    length_type: str = Query(..., description="Type of distance metric"),
    max_distance: int = Query(..., description="Maximum distance for isochrones"),
    k: int = Query(..., description="A parameter controlling the rate of decrease in accessibility beyond half of the maximum distance"), 
    max_amenities: int = Query(..., description="Sets the point of saturation. Only this amount of amenities will contribute to the index."),
    f: float = Query(..., description="A parameter controlling the rate at which the value of having additional amenities diminishes"),
):
    G = PedestrianGraph.load_graph(data_dir='data', filename='extended_network')
    source_point = Point(x, y)
    proximity_dict = G.get_closeby_amenities(source_point, length_type, max_distance)

    return compute_accessibility_index(proximity_dict, max_distance, k, max_amenities, f)

@router.get("/residential_buildings_with_accessibility_index")
# http://localhost:8000/residential_buildings_with_accessibility_index?urban_planning_unit_id=21&length_type=length_m&max_distance=1000&k=100&max_amenities=3&f=0.2
async def residential_buildings_with_accessibility_index(
    urban_planning_unit_id: int = Query(..., description="GID of a planning unit"),
    length_type: str = Query(..., description="Type of distance metric"),
    max_distance: int = Query(..., description="Maximum distance for isochrones"),
    k: int = Query(..., description="A parameter controlling the rate of decrease in accessibility beyond half of the maximum distance"), 
    max_amenities: int = Query(..., description="Sets the point of saturation. Only this amount of amenities will contribute to the index."),
    f: float = Query(..., description="A parameter controlling the rate at which the value of having additional amenities diminishes"),
):
    G = PedestrianGraph.load_graph(data_dir='data', filename='extended_network')
    with_index = residential_buildings_service.get_with_accessibility(G, length_type, max_distance, k, max_amenities, f, urban_planning_unit_id)

    return {
        "type": "FeatureCollection",
        "features": with_index
    }

# @router.get("/get_isochrone")
# # http://localhost:8000/get_isochrone?x=316221.88866994827&y=4729194.708270278&length_type=length_m&max_distance=1000
# async def get_isochrones(
#     x: float = Query(..., description="X coordinate of the point"),
#     y: float = Query(..., description="Y coordinate of the point"),
#     length_type: str = Query("length_m", description="Type of distance metric"),
#     max_distance: int = Query(1000, description="Maximum distance for isochrones"),
# ):
#     G = PedestrianGraph.load_graph(data_dir='data', filename='extended_network')
#     source_point = Point(x, y)
#     isochrones = G.compute_isochrone(source_point, length_type, max_distance)

#     return mapping(isochrones)

# @router.get("/get_isochrones")
# # http://localhost:8000/get_isochrones?x=316221.88866994827&y=4729194.708270278&length_type=length_m&max_distance=1000&interval=200
# async def get_isochrones(
#     x: float = Query(..., description="X coordinate of the point"),
#     y: float = Query(..., description="Y coordinate of the point"),
#     length_type: str = Query("length_m", description="Type of distance metric"),
#     max_distance: int = Query(1000, description="Maximum distance for isochrones"),
#     interval: int = Query(100, description="Interval for isochrone calculation"),
# ):
#     G = PedestrianGraph.load_graph(data_dir='data', filename='extended_network')
#     source_point = Point(x, y)
#     isochrones = G.compute_isochrones(source_point, length_type, max_distance, interval)

#     return {key: mapping(value) for key, value in isochrones.items()}
