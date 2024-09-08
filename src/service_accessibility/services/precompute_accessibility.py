from .network import PedestrianGraph
from ..database.connection import get_db_session
from ..models.residential import Residential
from geoalchemy2.shape import to_shape
from .walkability_service import compute_accessibility_index
from .network import PedestrianGraph
import sqlalchemy as sa
import re

def process_building(building, G, length_type, max_distance, k, max_amenities, f):
    """Compute accessibility score for a building."""
    centroid = to_shape(building.geom).centroid
    proximity_dict = G.get_closeby_amenities(centroid, length_type, max_distance)

    return compute_accessibility_index(proximity_dict, max_distance, k, max_amenities, f)

def sanitize_column_name(length_type, max_distance, k, max_amenities, f):
    """Sanitize column names to follow PostgreSQL naming rules."""
    column_name = f"{length_type}_{max_distance}_{k}_{max_amenities}_{f}"
    column_name = re.sub(r'[^a-zA-Z0-9_]', '_', column_name)  # Replace invalid chars
    return column_name[:63]  # PostgreSQL column name limit is 63 characters

def create_table_and_index(schema, table_name):
    session = get_db_session()
    
    session.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS {schema};'))
    
    session.execute(sa.text(f'''
        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            building_gid INTEGER PRIMARY KEY,
            UNIQUE(building_gid)
        );
    '''))

    session.execute(sa.text(f'''
        CREATE INDEX IF NOT EXISTS idx_{table_name}_building_gid 
        ON {schema}.{table_name} (building_gid);
    '''))

    query = sa.text(f"SELECT COUNT(*) FROM {schema}.{table_name}")
    records_count = session.execute(query).scalar()

    if records_count == 0:
      copy_building_gid_from_building_table = f"""
          INSERT INTO {schema}.{table_name} (building_gid)
          SELECT gid
          FROM raw.buildings_all_residential_2024;

      """
      session.execute(sa.text(copy_building_gid_from_building_table))

    session.commit()
    session.close()

def check_column_exists(schema, table_name, column_name, drop=False):
    session = get_db_session()

    if drop:
        drop_column_query = sa.text(f'''
            ALTER TABLE {schema}.{table_name}
            DROP COLUMN IF EXISTS {column_name};
        ''')
  
        session.execute(drop_column_query)
        exsists = False
    else:
        check_query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = '{schema}' 
            AND table_name = '{table_name}'
            AND column_name = '{column_name}'
        );
        """
  
        exsists = session.execute(sa.text(check_query)).scalar()

    session.commit()
    session.close()

    return exsists

def compute_and_store_accessibility(length_type, max_distance, k, max_amenities, f, recompute=False):
    schema = 'results'
    table_name = 'building_accessibility'
    G = PedestrianGraph.load_graph(data_dir='data', filename='extended_network')

    session = get_db_session()

    column_name = sanitize_column_name(length_type, max_distance, k, max_amenities, f)

    create_table_and_index(schema, table_name)

    if check_column_exists(schema, table_name, column_name, drop=recompute):
        print(f"Column {column_name} already exists. Exiting.")
        return

    query = session.query(Residential.gid, Residential.geom)
    buildings = query.all()

    # Compute accessibility index for each building
    scores = []
    for building in buildings:
        score = process_building(building, G, length_type, max_distance, k, max_amenities, f)
        scores.append((building.gid, score))

    alter_table_query = f"""
    ALTER TABLE {schema}.{table_name}
    ADD COLUMN IF NOT EXISTS {column_name} NUMERIC;
    """
    session.execute(sa.text(alter_table_query))

    update_query = f"""
    UPDATE {schema}.{table_name} 
    SET {column_name} = data.score
    FROM (VALUES {', '.join([f"({gid}, {score})" for gid, score in scores])}) AS data(building_gid, score)
    WHERE {schema}.{table_name}.building_gid = data.building_gid;
    """

    session.execute(sa.text(update_query))
    session.commit()
    session.close()

    print(f"Successfully computed and saved accessibility scores in column {column_name}.")

def get_buildings_with_precomputed_accessibility(length_type, max_distance, k, max_amenities, f):
    column_name = sanitize_column_name(length_type, max_distance, k, max_amenities, f)

    session = get_db_session()

    sql = f'''
      WITH accessibility_subquery AS (
      SELECT
          building_accessibility.building_gid,
          building_accessibility.{column_name} AS accessibility_index
      FROM
          results.building_accessibility
      )
      SELECT
          r.gid,
          ST_AsText(r.geom) as geom,
          r.floorcount,
          r.appcount,
          accessibility_subquery.accessibility_index
      FROM
          raw.buildings_all_residential_2024 AS r
      JOIN
          accessibility_subquery
      ON
          r.gid = accessibility_subquery.building_gid;
    ''' 

    result = session.execute(sa.text(sql))

    return result.fetchall()