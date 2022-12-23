import os
import xml.etree.ElementTree as ET
import sys
import re


class InvalidFileException(Exception):
    pass


class ParsedGxlGraph:
    def __init__(self, path_to_gxl: str, color_by_feature: str = None) -> None:
        """
        This class contains all the information encoded in a single gxl file = one graph

        :param path_to_gxl: path to the gxl file
        :param color_by_feature: modify the color of the nodes
        """
        self.filepath = path_to_gxl

        self.filename = os.path.basename(self.filepath)
        # name of the gxl file (without the ending)
        self.file_id = self.filename[:-4]

        self.color_by_feature = color_by_feature

        # parsing the gxl
        # sets up the following properties: node_features, node_feature_names, edges, edge_features, edge_feature_names,
        # node_position, graph_id, edge_ids_present and edgemode
        self.setup_graph_features()

    @property
    def filepath(self) -> str:
        return self._filepath

    @filepath.setter
    def filepath(self, path_to_gxl):
        if not os.path.isfile(path_to_gxl):
            print(f'File {path_to_gxl} does not exist.')
            sys.exit(-1)
        self._filepath = path_to_gxl

    @property
    def nb_of_nodes(self):
        return len(self.node_features)

    @property
    def nb_of_edges(self):
        return len(self.edge_features)

    def setup_graph_features(self):
        """
        Parses the gxl file and sets the following graph properties
        - graph info: graph_id, edge_ids_present and edgemode
        - node: node_features, node_feature_names, and node_position
        - edge: edges, edge_features and edge_feature_names

        """
        tree = ET.parse(self.filepath)
        root = tree.getroot()

        # verify that the file contains the expected attributes (node, edge, id, edgeids and edgemode)
        self.sanity_check(root)

        self.graph_id, self.edge_ids_present, self.edgemode = self.get_graph_attr(root)  # (str, bool, str)

        # nodes
        self.node_feature_names, self.node_features, min_node_id = self.get_node_features(root)  # ([str], list)

        # Add the coordinates to their own variable
        if self.node_feature_names is None or 'x' not in self.node_feature_names and 'y' not in self.node_feature_names:
            print('Graph does not contain x or y coordinates as features. '
                  'Coordinates have to be specified in the gxl file as "x" and "y".')

        x_ind = self.node_feature_names.index('x')
        y_ind = self.node_feature_names.index('y')

        self.node_positions = [[node[x_ind], node[y_ind]] for node in self.node_features]
        if self.color_by_feature:
            self.color_by_features = [node[self.node_feature_names.index(self.color_by_feature)] for node in
                                      self.node_features]

        # edges
        self.edges = self.get_edges(root, shift=min_node_id)  # [[int, int]]
        self.edge_feature_names, self.edge_features = self.get_edge_features(root)  # ([str], list)

    def get_node_feature_values(self, feature) -> list:
        """
        Get the feature values of the nodes for a given feature name
        :param feature: feature name
        :return: list [feature of node 1, feature of node 2, ...]
        """
        feature_ind = self.node_feature_names.index(feature)
        all_features = [nf[feature_ind] for nf in self.node_features]
        return all_features

    def get_edge_feature_values(self, feature) -> list:
        """
        Get the feature values of the edges for a given feature name
        :param feature: feature name
        :return: list [feature of edge 1, feature of edge 2, ...]
        """
        feature_ind = self.edge_features.index(feature)
        all_features = [[nf][feature_ind] for nf in self.edge_features]
        return all_features

    def get_features(self, root, mode):
        """
        Get a list of the node or edge features out of the element tree (gxl)
        :param root: root of ET tree
        :param mode: either 'edge' or 'node'
        :return:  tuple ([str], [[mixed values]])
            list of all node features for that tree
            ([feature name 1, feature name 2, ...],  [[feature 1 of node 1, feature 2 of node 1, ...], [feature 1 of node 2, ...], ...])
        """
        features_info = [[feature for feature in graph_element] for graph_element in root.iter(mode)]
        if len(features_info) > 0:
            feature_names = [i.attrib['name'] for i in features_info[0]]
        else:
            feature_names = []

        # check if we have features to generate
        if len(feature_names) > 0:
            features = [[self.decode_feature(value) for feature in graph_element for value in feature if
                         feature.attrib['name'] in feature_names] for graph_element in root.iter(mode)]
        else:
            feature_names = None
            features = []

        return feature_names, features

    def get_node_features(self, root) -> tuple:
        """
        Get node feature names/values and the smallest id
        :param root: root of ET tree
        :return: tuple  ([str], [[mixed values]], int)
            list of all node features and the minimal id
        """
        # minimal node id -> used to shift the edge indexing to 0 (in case node enumeration does not start with 0)
        regex = r'_(\d+)$'
        node_ids = [int(re.search(regex, graph_element.attrib['id']).group(1)) for graph_element in root.iter('node')]
        feature_names, features = self.get_features(root, 'node')
        return feature_names, features, min(node_ids)

    def get_edge_features(self, root) -> tuple:
        """
        Get edge feature names/values
        :param root: root of ET tree
        :return: tuple  ([str], [[mixed values]], int)
            list of all edge features
        """
        feature_names, features = self.get_features(root, 'edge')
        return feature_names, features

    def sanity_check(self, root):
        """
        Check if files contain the expected content
        :param root: root of ET tree
        """
        # check if node, edge, edgeid, edgemode, edgemode keyword exists
        if len([i.attrib for i in root.iter('graph')][0]) != 3:
            raise InvalidFileException

        if len([node for node in root.iter('node')]) == 0:
            print(f'File {os.path.basename(self.filepath)} is an empty graph!')
            raise InvalidFileException
        elif len([edge for edge in root.iter('edge')]) == 0:
            print(f'File {os.path.basename(self.filepath)} has no edges!')

    @staticmethod
    def get_graph_attr(root) -> tuple:
        """
        Get the information attributes of the whole graph
        :param root: root of ET tree
        :return: tuple (str, bool, str)
            ID of the graph, Edge IDs present (true / false), edge mode (directed / undirected)
        """
        graph = [i.attrib for i in root.iter('graph')]
        assert len(graph) == 1
        g = graph[0]
        return g['id'], g['edgeids'] == 'True', g['edgemode']

    @staticmethod
    def get_edges(root, shift=0) -> list:
        """
        Get the start and end points of every edge and store them in a list of lists (from the element tree, gxl)
        :param root: root of ET tree
        :param shift: int, if the smallest id of the nodes is not 0, then shift the edge indexing to start from 0.
        :return: [[int, int]]
            list of indices of connected nodes
        """
        edge_list = []

        regex = r'_(\d+)$'
        start_points = [int(re.search(regex, edge.attrib['from']).group(1)) for edge in root.iter('edge')]
        end_points = [int(re.search(regex, edge.attrib['to']).group(1)) for edge in root.iter('edge')]
        assert len(start_points) == len(end_points)

        # move enumeration start to 0 if necessary
        if len(start_points) > 0 and len(end_points) > 0:
            if shift != 0:
                start_points = [x - shift for x in start_points]
                end_points = [x - shift for x in end_points]
            edge_list = [[start_points[i], end_points[i]] for i in range(len(start_points))]

        return edge_list

    @staticmethod
    def decode_feature(f):
        data_types = {'string': str,
                      'float': float,
                      'int': int}

        # convert the feature value to the correct data type as specified in the gxl
        return data_types[f.tag](f.text.strip())
