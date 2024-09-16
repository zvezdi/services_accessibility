from ..database.connection import get_db_session
from ..models.urban_planning_unit import UrbanPlanningUnit
from geoalchemy2.shape import to_shape
from shapely import wkt
from shapely.geometry import mapping
from .crs_transform import get_transformer, crs_transform

def get_all():
    session = get_db_session()
    try:
        urban_planning_units = session.query(UrbanPlanningUnit).all()
        transformer = get_transformer()
        return [
            {
                "type": "Feature",
                "geometry": mapping(crs_transform(transformer, to_shape(urban_planning_unit.geom), swap_coords=False)),
                "properties": {
                    "gid": urban_planning_unit.gid,
                    "name": urban_planning_unit.regname,
                    "district": urban_planning_unit.rajon,
                }
            }
            for urban_planning_unit in urban_planning_units
        ]
    finally:
        session.close()

def upus_to_geojson(upus):
    transformer = get_transformer()
    return(
        {
            "type": "Feature",
            "geometry": mapping(crs_transform(transformer, wkt.loads(upu.geom), swap_coords=False)),
            "properties": {
                "gid": upu.gid,
                "floorcount": upu.floor_count,
                "buildingcount": upu.building_count,
                "accessibility": upu.accessibility_index,
                "appcount": upu.app_count,
            }
        }
        for upu in upus
    )
