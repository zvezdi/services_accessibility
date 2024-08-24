from typing import Dict, Any, Tuple
import networkx as nx
from rtree import index
import pickle
import os
from geoalchemy2.shape import to_shape
from shapely.geometry import LineString, MultiLineString, Point, Polygon, MultiPoint
from shapely import wkt
from ..database.connection import get_db_session
from ..models.pedestrian_path import PedestrianPath
from .crs_transform import get_transformer, crs_transform
from tqdm import tqdm

class PedestrianGraph:
    POINT_BUFFER = 2.0  # 2 meter buffer as rtree requires a rectangle to work with

    def __init__(self):
        self.G = nx.Graph()
        self.rtree_nodes_index = index.Index()
        self.rtree_edges_index = index.Index()
        self.node_id_counter = 0
        self.edge_id_counter = 0
        self.edge_id_to_nodes = {}  # Mapping from edge_id to (start_node, end_node)
        self.nodes_to_edge_id = {}  # Mapping from (start_node, end_node) to edge_id

    def save_graph(self, filename: str):
        """
        Save the graph and its spatial indices to disk.
        """
        data_dir = 'data'
        nodes_idx_filename = os.path.join(data_dir, f'{filename}_spatial_index_nodes')
        edges_idx_filename = os.path.join(data_dir, f'{filename}_spatial_index_edges')
        graph_filename = os.path.join(data_dir, f'{filename}.gpickle')

        # Close the R-tree indices before saving
        self.rtree_nodes_index.close()
        self.rtree_edges_index.close()
        
        with open(graph_filename, 'wb') as f:
            pickle.dump((self.G, self.node_id_counter, self.edge_id_counter, self.edge_id_to_nodes, self.nodes_to_edge_id), f)

        # Re-load the R-tree index from disk
        self.rtree_nodes_index = index.Index(nodes_idx_filename)
        self.rtree_edges_index = index.Index(edges_idx_filename)

    @classmethod
    def load_graph(cls, filename: str):
        data_dir = 'data'
        nodes_idx_filename = os.path.join(data_dir, f'{filename}_spatial_index_nodes')
        edges_idx_filename = os.path.join(data_dir, f'{filename}_spatial_index_edges')
        graph_filename = os.path.join(data_dir, f'{filename}.gpickle')

        if not os.path.exists(graph_filename):
            return None

        pedestrian_graph = cls()
        with open(graph_filename, 'rb') as f:
            pedestrian_graph.G, pedestrian_graph.node_id_counter, pedestrian_graph.edge_id_counter, pedestrian_graph.edge_id_to_nodes, pedestrian_graph.nodes_to_edge_id = pickle.load(f)

        pedestrian_graph.rtree_nodes_index = index.Index(nodes_idx_filename)
        pedestrian_graph.rtree_edges_index = index.Index(edges_idx_filename)

        return pedestrian_graph

    def build_pedestrian_graph(self, load: bool=False, filename='pedestrian_graph'):
        if load:
            loaded_graph = self.load_graph(filename)
            if loaded_graph:
                self = loaded_graph
                return

        session = get_db_session()
        pedestrian_networks = session.query(PedestrianPath).all()
        
        for path in pedestrian_networks:
            geom = to_shape(path.geom)
            
            if isinstance(geom, LineString):
                self.add_linestring_to_graph(geom, path)
            elif isinstance(geom, MultiLineString):
                for linestring in geom.geoms:
                    if isinstance(linestring, LineString):
                        self.add_linestring_to_graph(linestring, path)
                    else:
                        raise ValueError(f'{linestring} is not a Linestring, valid: {linestring.is_valid}')

    def get_edge_id(self, start_node: int, end_node: int) -> int:
        if (start_node, end_node) in self.nodes_to_edge_id:
            return self.nodes_to_edge_id[(start_node, end_node)]
        elif (end_node, start_node) in self.nodes_to_edge_id:
            return self.nodes_to_edge_id[(end_node, start_node)]
        else:
            edge_id = self.edge_id_counter
            self.edge_id_counter += 1
            self.edge_id_to_nodes[edge_id] = (start_node, end_node)
            self.nodes_to_edge_id[(start_node, end_node)] = edge_id
            self.nodes_to_edge_id[(end_node, start_node)] = edge_id  # undirected graph
            return edge_id

    def add_linestring_to_graph(self, linestring: LineString, path: PedestrianPath):
        start_point = Point(linestring.coords[0])
        end_point = Point(linestring.coords[-1])
        
        start_node_id = self.add_or_get_node(start_point)
        end_node_id = self.add_or_get_node(end_point)
        
        if start_node_id == end_node_id:
            # TODO: Figure out why we get edges linestrings that have the same start and end point
            return

        self.G.add_edge(
            start_node_id,
            end_node_id,
            length_m=path.length_m,
            minutes=path.minutes,
        )

        edge_id = self.get_edge_id(start_node_id, end_node_id)
        self.rtree_edges_index.insert(edge_id, linestring.bounds)

    def add_or_get_node(self, point: Point, amenity_type=None) -> int:
        # Check if a node already exists at this point
        nearest = list(self.rtree_nodes_index.nearest(point.bounds, 1))
        if nearest:
            existing_node_id = nearest[0]
            existing_point = wkt.loads(self.G.nodes[existing_node_id]['wkt'])
            if existing_point.equals(point):
                # If the node already exists and doesn't have an amenity type, add it
                # TODO: Add support for 2 different amenities at the same point 
                if amenity_type and 'amenity_type' not in self.G.nodes[existing_node_id]:
                    self.G.nodes[existing_node_id]['amenity_type'] = amenity_type
                return existing_node_id

        # If no existing node, create a new one
        new_node_id = self.node_id_counter
        self.node_id_counter += 1
        node_data = {'wkt': point.wkt}
        if amenity_type:
            node_data['amenity_type'] = amenity_type
        self.G.add_node(new_node_id, **node_data)
        self.rtree_nodes_index.insert(new_node_id, point.buffer(self.POINT_BUFFER).bounds)
        return new_node_id

    def node_to_point(self, node_id: int) -> Point:
        if self.G.has_node(node_id):
            return wkt.loads(self.G.nodes[node_id]['wkt'])
        else:
            raise ValueError(f"Node {node_id} does not exist in the graph.")

    def find_nearest_node(self, point: Point) -> int:
        nearest_node_candidates = list(self.rtree_nodes_index.nearest(point.bounds, 10))
        if not nearest_node_candidates:
            raise ValueError("No nodes found in the graph.")

        return min(nearest_node_candidates, key=lambda n: self.node_to_point(n).distance(point))

    def find_nearest_edge(self, point: Point) -> Tuple[int, int]:
        nearest_edges_candidates = list(self.rtree_edges_index.nearest(point.bounds, 20))

        min_distance = float('inf')
        nearest_edge = None

        for edge_id in nearest_edges_candidates:
            if not edge_id in self.edge_id_to_nodes:
                print(f'Skipping edge_id {edge_id} from nearest_edges_candidates')
                continue
            start_node_id, end_node_id = self.edge_id_to_nodes[edge_id]
            start_point = self.node_to_point(start_node_id)
            end_point = self.node_to_point(end_node_id)
            line = LineString([start_point, end_point])

            distance = line.distance(point)
            if distance < min_distance:
                min_distance = distance
                nearest_edge = (start_node_id, end_node_id)

        if nearest_edge is None:
            raise ValueError("No edges found in the graph.")

        return nearest_edge

    def extend_graph_with_point(self, point: Point, amenity_type=None) -> int:
        start_node_id, end_node_id = self.find_nearest_edge(point)
        if start_node_id == end_node_id:
            # TODO: Double check
            return

        edge_data = self.G[start_node_id][end_node_id]

        start_point = self.node_to_point(start_node_id)
        end_point = self.node_to_point(end_node_id)
        edge_line = LineString([start_point, end_point])

        projected_point = edge_line.interpolate(edge_line.project(point))
        new_node_id = self.add_or_get_node(point, amenity_type)
        projected_node_id = self.add_or_get_node(projected_point)

        self.G.remove_edge(start_node_id, end_node_id)

        new_edge_from_point_to_projection = LineString([point, projected_point])
        new_edge_1 = LineString([start_point, projected_point])
        new_edge_2 = LineString([projected_point, end_point])

        length_from_point_to_projection = new_edge_from_point_to_projection.length
        total_length = edge_data['length_m']
        proportion_1 = new_edge_1.length / total_length if total_length != 0 else 0
        proportion_2 = new_edge_2.length / total_length if total_length != 0 else 0

        self.G.add_edge(
            start_node_id,
            projected_node_id, 
            length_m=edge_data['length_m'] * proportion_1,
            minutes=edge_data['minutes'] * proportion_1
        )
        
        self.G.add_edge(
            projected_node_id, 
            end_node_id,
            length_m=edge_data['length_m'] * proportion_2,
            minutes=edge_data['minutes'] * proportion_2
        )
        
        self.G.add_edge(
            new_node_id, 
            projected_node_id, 
            length_m=length_from_point_to_projection,
            minutes=length_from_point_to_projection / edge_data['max_speed'] if 'max_speed' in edge_data else 1
        )
        
        old_edge_id = self.get_edge_id(start_node_id, end_node_id)
        self.rtree_edges_index.delete(old_edge_id, self.edge_id_to_nodes[old_edge_id])
        del self.edge_id_to_nodes[old_edge_id]
        del self.nodes_to_edge_id[(start_node_id, end_node_id)]
        del self.nodes_to_edge_id[(end_node_id, start_node_id)]

        new_edge_id_1 = self.get_edge_id(start_node_id, projected_node_id)
        new_edge_id_2 = self.get_edge_id(projected_node_id, end_node_id)
        new_edge_id_3 = self.get_edge_id(new_node_id, projected_node_id)

        self.rtree_edges_index.insert(new_edge_id_1, new_edge_1.bounds)
        self.rtree_edges_index.insert(new_edge_id_2, new_edge_2.bounds)
        self.rtree_edges_index.insert(new_edge_id_3, new_edge_from_point_to_projection.bounds)

        return new_node_id

    def extend_graph_with(self, locations, amenity_type = None):
        total_locations = len(locations)
        
        with tqdm(total=total_locations, desc="Extending graph", unit="location") as pbar:
            for location in locations:
                shape = to_shape(location.geom)
                if isinstance(shape, Point):
                    # There are 3D Multipoints in the database
                    simple_point = Point(shape.x, shape.y)
                    self.extend_graph_with_point(simple_point, amenity_type)
                elif isinstance(shape, MultiPoint):
                    for point in shape.geoms:
                        # There are 3D Multipoints in the database
                        simple_point = Point(point.x, point.y)
                        self.extend_graph_with_point(simple_point, amenity_type)
                else:
                    pbar.write(f"Skipping unsupported geometry type: {type(shape)}")
                pbar.update(1)
        
        print(f"Graph extension completed. Processed {total_locations} locations.")

    def graph_to_geojson(self) -> Dict:
        features = []
        transformer = get_transformer()
        for u, v, data in self.G.edges(data=True):
            start_point = self.node_to_point(u)
            end_point = self.node_to_point(v)
            linestring = LineString([start_point, end_point])
            geom_in_world_crs = crs_transform(transformer, linestring, swap_coords=False)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": list(geom_in_world_crs.coords)
                },
                "properties": {
                    "length_m": data['length_m'],
                    "minutes": data['minutes'],
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
