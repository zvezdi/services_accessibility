from fastapi import APIRouter, HTTPException
from ..services import school_service
from ..services import urban_planning_unit_service

from ..services.network import PedestrianGraph

router = APIRouter()

@router.get("/pedestrian_network")
async def get_pedestrian_network():
    G = PedestrianGraph.load_graph('extended_network')
    return G.graph_to_geojson()


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

# @router.get("/schools/accessibility")
# async def get_schools_accessibility_isochrons():
#     schools_isochrones = school_service.get_schools_accesibility_isochrones()
#     return {
#         "type": "FeatureCollection",
#         "features": schools_isochrones
#     }
    