import cv2

from util.gxl_graph import ParsedGxlGraph
from util.draw_graph import GraphDrawer


def graph_plotter(gxl_filepath, img_filepath, color_by_feature, node_style, edge_style, scaling, transparency,
                  current_node):
    """
    This function draws a graph on an image.

    :param gxl_filepath: path to the gxl file with the graph
    :param img_filepath: path to the corresponding image file
    :param color_by_feature: name of the feature the nodes should be colored by
    :param node_style: dictionary with the node style (color and radius)
    :param edge_style: color and thickness of edges (color and thickness)
    :param scaling: x,y coordinates will be scaled accordingly (in case they are not in pixel)
    :param transparency: transparency of the image
    :param current_node: the current node selected in the node style option menu
    """

    graph = ParsedGxlGraph(gxl_filepath, color_by_feature=color_by_feature)
    img = cv2.imread(img_filepath)

    graph_img = GraphDrawer(graph, img, scaling=scaling, color_by_feature=color_by_feature,
                            node_style=node_style, edge_style=edge_style,
                            transparency=transparency, current_node=current_node)

    return graph_img

