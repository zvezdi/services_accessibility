from ..database.connection import get_db_session
from ..models.school import School
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

def get_all_schools():
    session = get_db_session()
    try:
        schools = session.query(School).all()
        return [
            {
                "type": "Feature",
                "geometry": mapping(to_shape(school.geom)),
                "properties": {
                    "gid": school.gid,
                    "subgroup": school.subgroup_i
                }
            }
            for school in schools
        ]
    finally:
        session.close()
