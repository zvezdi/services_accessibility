from .network import PedestrianGraph
from ..database.connection import get_db_session
from ..models.point_of_interest import CulturePOI, HealthPOI, KidsPOI, MobilityPOI, SchoolPOI, ServicePOI, GreenPOI, SportPOI 
from ..models.residential import Residential
from sqlalchemy import func

def build_and_save(filename: str):
    pedestrian_graph = PedestrianGraph()
    pedestrian_graph.build_pedestrian_graph()
    
    poi_types = [CulturePOI, HealthPOI, KidsPOI, MobilityPOI, SchoolPOI, ServicePOI, GreenPOI, SportPOI]

    session = get_db_session()
    for poi_type in poi_types:
        pois = session.query(
            poi_type.subgroup_i,
            func.array_agg(poi_type.gid).label('poi_ids')  # Aggregate the IDs
        ).group_by(poi_type.subgroup_i).all()
        
        for subgroup, poi_ids in pois:
            # Query the full objects based on the aggregated IDs
            grouped_pois = session.query(poi_type).filter(poi_type.gid.in_(poi_ids)).all()
            pedestrian_graph.extend_graph_with(grouped_pois, amenity_type=subgroup)

    residential_buildings = session.query(Residential).all()
    pedestrian_graph.extend_graph_with(residential_buildings)
    pedestrian_graph.save_graph(filename)
