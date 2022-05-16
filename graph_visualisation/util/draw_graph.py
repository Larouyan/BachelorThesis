import os
import cv2
import matplotlib as mpl
from matplotlib import cm


class MplColorHelper:
    def __init__(self, cmap_name, nb_colors):
        self.cmap_name = cmap_name
        self.cmap = cm.get_cmap(cmap_name)
        self.norm = mpl.colors.Normalize(vmin=0, vmax=nb_colors - 1)
        self.scalarMap = cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    def get_rgb(self, val):
        return tuple([int(c * 255) for c in self.scalarMap.to_rgba(val)][:3])


class GraphDrawer:
    def __init__(self, graph, img, color_by_feature, node_style, edge_style, scaling,
                 transparency, current_node) -> None:
        """
        This class draws the graph on the image

        :param graph: parsed GxlGraph
        :param img: image that the graphs is drawn on
        :param color_by_feature: name of the feature to color by
        :param node_style: dictionary with the node style
        :param edge_style: dictionary with the edge style
        :param scaling: scaling for the x,y coordinates (in case they are not in pixels)
        :param transparency: transparency of the original image
        :param current_node: the current node selected in the node style option menu
        """
        self.transparency = transparency
        self.graph = graph
        self.img = img
        self.scaling = scaling
        self.id = graph.file_id
        self.color_by_feature = color_by_feature
        self.current_node = current_node

        self.node_style = node_style
        self.edge_style = edge_style

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, img):
        # Add alpha layer
        bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        # Set alpha layer semi-transparent with Numpy indexing, B=0, G=1, R=2, A=3
        bgra[..., 3] = self.transparency
        self._img = bgra

    @property
    def node_style(self) -> dict:
        return self._node_config

    @node_style.setter
    def node_style(self, node_config):
        default = {'color': (47, 130, 224, 255), 'radius': 20, 'thickness': -1}
        if node_config is None:
            if self.color_by_feature is None:
                node_config = default
            else:
                nb_diff_features = sorted(list(set(self.graph.color_by_features)))
                color_mixer = MplColorHelper('Spectral', len(nb_diff_features))
                node_config = {f: {'color': color_mixer.get_rgb(i), 'radius': 20} for i, f in
                               enumerate(nb_diff_features)}
                node_config['thickness'] = -1

        self._node_config = node_config

    @property
    def edge_style(self) -> dict:
        return self._edge_config

    @edge_style.setter
    def edge_style(self, edge_config):
        default = {'color': (30, 110, 30, 255), 'thickness': 10, 'lineType': cv2.LINE_AA}  #
        if edge_config is None:
            edge_config = default
        elif len(edge_config) != default:
            for k, v in default.items():
                if k not in edge_config:
                    edge_config[k] = v

        self._edge_config = edge_config

    def get_image(self):
        img = self.img
        points = {i: tuple([int(x_y[0] * self.scaling), int(x_y[1] * self.scaling)]) for i, x_y in
                  enumerate(self.graph.node_positions)}

        # draw the edges
        for edge in self.graph.edges:
            pt1, pt2 = (points[edge[0]], points[edge[1]])
            img = cv2.line(img, pt1, pt2, color=self.edge_style['color'], thickness=self.edge_style['thickness'],
                           lineType=self.edge_style['lineType'])

        # draw the points (according to the type, if applicable)
        if self.color_by_feature:
            for feature, (i, point) in zip(self.graph.color_by_features, points.items()):
                img = cv2.circle(img, point, radius=self.node_style[feature]['radius'],
                                 color=self.node_style[feature]['color'],
                                 thickness=self.node_style['thickness'])
        else:
            # default = {'color': (47, 130, 224, 255), 'radius': 20, 'thickness': -1}
            for i, point in points.items():
                img = cv2.circle(img, point, radius=self.node_style[self.current_node]['radius'],
                                 color=self.node_style[self.current_node]['color'],
                                 thickness=self.node_style['thickness'])

        return img

    def save(self, output_path: str):
        output_file = os.path.join(output_path, f'{self.id}-vis.png')
        cv2.imwrite(output_file, cv2.cvtColor(self.get_image(), cv2.COLOR_RGB2BGR))
        print(f'Visualization saved to {output_file}')
