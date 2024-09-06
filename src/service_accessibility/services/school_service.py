from ..database.connection import get_db_session
from ..models.point_of_interest import SchoolPOI
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from .crs_transform import get_transformer, crs_transform
# from .network import build_pedestrian_graph, extend_graph_with, compute_accessibility_isochrone

import logging

logging.basicConfig(level=logging.ERROR)

def get_all():
    session = get_db_session()
    try:
        schools = session.query(SchoolPOI).all()
        transformer = get_transformer()
        return [
            {
                "type": "Feature",
                "geometry": mapping(crs_transform(transformer, to_shape(school.geom), swap_coords=False)),
                "properties": {
                    "gid": school.gid,
                    "subgroup": school.subgroup_i
                }
            }
            for school in schools
        ]
    finally:
        session.close()

# def compute_school_isochrone(G, school):
    # isochron = compute_accessibility_isochrone(G=G, source=school, weight_type='length', max_weight=1000)
    # print(isochron)
    # print("WHAT IS WRONG HERE?????")
    # return isochron

# def compute_schools_isochrones(db_session):
#     schools = db_session.query(School).all()
#     G = build_pedestrian_graph()
#     G = extend_graph_with(G, schools)
#     results = {}
#     for school in schools:
#         for max_length in [400, 800, 1600]:
#             polygon = compute_accessibility_isochrone(G, school, weight_type='length', max_weight=max_length)
#             results[school.uid][max_length] = polygon

#     #Update the schoold table in the database with the computed data

# def get_schools_accesibility_isochrones():
#     session = get_db_session()

#     schools = session.query(School).all()
#     G = build_pedestrian_graph()
#     # G = extend_graph_with(G, schools)
#     transformer = get_transformer()
    
#     return [
#         {
#             "type": "Feature",
#             "geometry": mapping(crs_transform(transformer, compute_school_isochrone(G, school.geom), swap_coords=False)),
#             "properties": {
#                 "gid": school.gid,
#                 "subgroup": school.subgroup_i
#             }
#         }
#         for school in schools
#     ]
