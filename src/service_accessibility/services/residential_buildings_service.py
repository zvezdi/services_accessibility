from ..database.connection import get_db_session
from ..models.residential import Residential
from ..models.urban_planning_unit import UrbanPlanningUnit
from geoalchemy2.shape import to_shape
from shapely import wkt
from shapely.geometry import mapping
from .crs_transform import get_transformer, crs_transform
from .walkability_service import compute_accessibility_index
from geoalchemy2 import functions as gfunc

from multiprocessing import Pool, cpu_count

def get_all():
    session = get_db_session()
    try:
        residential_buildings = session.query(Residential).all()
        transformer = get_transformer()
        return [
            {
                "type": "Feature",
                "geometry": mapping(crs_transform(transformer, to_shape(building.geom), swap_coords=False)),
                "properties": {
                    "gid": building.gid,
                    "floorcount": building.floorcount,
                    "appcount": building.appcount,
                }
            }
            for building in residential_buildings
        ]
    finally:
        session.close()

def process_building(building, G, transformer, length_type, max_distance, k, max_amenities, f):
    centroid = to_shape(building.geom).centroid
    proximity_dict = G.get_closeby_amenities(centroid, length_type, max_distance)
    index = compute_accessibility_index(proximity_dict, max_distance, k, max_amenities, f)
    
    building_features = {
        "type": "Feature",
        "geometry": mapping(crs_transform(transformer, centroid, swap_coords=False)),
        "properties": {
            "gid": building.gid,
            "floorcount": building.floorcount,
            "appcount": building.appcount,
            "accessibility": index
        }
    }
    return building_features

def get_with_accessibility(G, length_type, max_distance, k, max_amenities, f, urban_planning_unit_id):

    session = get_db_session()
    try:
        if urban_planning_unit_id:
            query = (
                session.query(Residential)
                .join(
                    UrbanPlanningUnit,
                    gfunc.ST_Within(Residential.geom, UrbanPlanningUnit.geom)
                )
                .filter(UrbanPlanningUnit.gid == urban_planning_unit_id)
            )
        else:
            query= session.query(Residential.gid, Residential.geom, Residential.floorcount, Residential.appcount)
        
        residential_buildings = query.all()
        transformer = get_transformer()

        # Parallel processing with Pool
        with Pool(processes=cpu_count()) as pool:
            result = pool.starmap(
                process_building,
                [(building, G, transformer, length_type, max_distance, k, max_amenities, f) for building in residential_buildings]
            )

        return result
    finally:
        session.close()

def buildings_to_geojson(buildings):
    transformer = get_transformer()

    return(
        {
            "type": "Feature",
            "geometry": mapping(crs_transform(transformer, wkt.loads(building.geom).centroid, swap_coords=False)),
            "properties": {
                "gid": building.gid,
                "floorcount": building.floorcount,
                "appcount": building.appcount,
                "accessibility": building.accessibility_index,
            }
        }
        for building in buildings
    )