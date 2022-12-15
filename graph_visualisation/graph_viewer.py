import os
import re

from tkinter import *
from tkinter import filedialog, colorchooser

from PIL import ImageTk, Image

from graph_plotter import graph_plotter
from gui.tk_factory import TkFactory
from util.draw_graph import GraphDrawer
from util.gxl_graph import ParsedGxlGraph

# Import configuration of the nodes and edges
from util.default_config import node_style, edge_style


class GraphViewer:
    def __init__(self, img_dir, gxl_dir, color_by_feature, cb_blank, transparency, scaling, selected_node):
        self.img_dir = img_dir
        self.gxl_dir = gxl_dir
        self.color_by_feature = color_by_feature
        self.cb_blank = cb_blank
        self.transparency = transparency
        self.scaling = scaling
        self.selected_node = selected_node

        self.graph_img = GraphDrawer
        self.listbox_content = []

        self.components = dict()
        self.customizers = dict()

    def set_components_customizers(self, factory: TkFactory):
        self.components = factory.get_components()
        self.customizers = factory.get_customizers()

    def select_img_dir(self, *args):
        """
        Ask the user for the directory where the images are.
        """
        new_dir = filedialog.askdirectory()
        if new_dir:
            if os.path.isdir(new_dir):
                self.img_dir.set(new_dir)

    def select_gxl_dir(self, *args):
        """
        Ask the user for the directory where the gxl files are.
        """
        new_dir = filedialog.askdirectory()
        if new_dir:
            if os.path.isdir(new_dir):
                self.load_gxl_dir(new_dir)

    def load_gxl_dir(self, new_dir):
        """
        Load the gxl files on the listbox.
        :param new_dir: directory where the gxl files are.
        """
        self.gxl_dir.set(new_dir)
        listbox = self.components['gxl_listbox']
        # delete previous gxl dir
        listbox.delete(0, END)
        for file in sorted(os.listdir(new_dir)):
            if file.lower().endswith('.gxl'):
                if os.path.isfile(os.path.join(new_dir, file)):
                    listbox.insert(END, file.rsplit('.', 1)[0])
        if listbox.size() > 0:
            listbox.select_set(0)
            self.listbox_content = listbox.get(0, END)
            self.components['lb_entry']['state'] = NORMAL
            self.load_graph_features()
            # onselect()

    def update_gxl_listbox(self, pattern):
        """
        Update the list of gxl files such that it only display files that start with a given pattern.
        :param pattern: string given by the user.
        """
        listbox = self.components['gxl_listbox']
        listbox.delete(0, END)
        for file in self.listbox_content:
            if str(file).upper().startswith(pattern.get().upper()):
                listbox.insert(END, file)

    def load_graph_features(self):
        """
        Fill the option menu with the graph features in order to color the nodes by features.
        """
        parsed = ParsedGxlGraph(os.path.join(self.gxl_dir.get(), os.listdir(self.gxl_dir.get())[0]))
        features = [f for f in parsed.node_feature_names if f not in ['x', 'y']]
        for feature in features:
            cbf_menu = self.components['cbf_menu']
            cbf_menu['menu'].add_command(label=feature, command=lambda value=feature: self.color_by_feature.set(value))

    def get_color_by_feature(self):
        """
        :return: Selected feature modifying the 'None' string to None keyword.
        """
        if self.color_by_feature.get() == 'None':
            return None
        else:
            return self.color_by_feature.get()

    def save_img(self, *arg):
        """
        Save the current image in a directory chosen by the user.
        """
        output_path = filedialog.askdirectory()
        if output_path:
            if os.path.isdir(output_path):
                self.graph_img.save(output_path)

    def save_all(self, *args):
        """
        Save all images in a directory chosen by the user.
        """
        output_path = filedialog.askdirectory()
        if output_path:
            if os.path.isdir(output_path):
                for gxl_file in os.listdir(self.gxl_dir.get()):
                    gxl_filename = gxl_file.rsplit('.', 1)[0]
                    img_filepath = self.search_img_filepath(gxl_filename)
                    if img_filepath:
                        gxl_filepath = os.path.join(self.gxl_dir.get(), gxl_file)
                        temp_graph = graph_plotter(gxl_filepath=gxl_filepath, img_filepath=img_filepath,
                                                   color_by_feature=self.get_color_by_feature(),
                                                   node_style=node_style, edge_style=edge_style,
                                                   scaling=float(self.scaling.get()),
                                                   transparency=self.transparency.get(),
                                                   current_node=self.selected_node.get())
                        temp_graph.save(output_path)

    def search_img_filepath(self, gxl_filename):
        """
        Find the image corresponding to the gxl file given in input.
        :param gxl_filename: name of the gxl file.
        :return: The path to the corresponding image if it exists, otherwise it returns None.
        """
        extensions = ('png', 'bmp', 'jpg', 'jpeg', 'gif')

        for img in os.listdir(self.img_dir.get()):
            if re.match(r'.*' + re.escape(gxl_filename) + r'.*', img):
                for ext in extensions:
                    if img.endswith(ext):
                        return os.path.join(self.img_dir.get(), img)

        return None

    def onselect(self, *args):
        """
        Draw the image with the graph on the canvas
        """
        if self.img_dir.get() != '':
            canvas = self.components['canvas']
            canvas.delete("all")
            listbox = self.components['gxl_listbox']
            try:
                index = int(listbox.curselection()[0])
                gxl_filename = listbox.get(index)
            except IndexError:
                # If listbox is unselected then take the previous gxl file which was selected
                gxl_filename = self.graph_img.graph.file_id

            gxl_filepath = os.path.join(self.gxl_dir.get(), gxl_filename + '.gxl')
            img_filepath = self.search_img_filepath(gxl_filename)

            if img_filepath or (not img_filepath and self.cb_blank.get()):
                self.enable_customisation()

                self.graph_img = graph_plotter(gxl_filepath=gxl_filepath, img_filepath=img_filepath,
                                               color_by_feature=self.get_color_by_feature(),
                                               node_style=node_style, edge_style=edge_style,
                                               scaling=float(self.scaling.get()), transparency=self.transparency.get(),
                                               current_node=self.selected_node.get())
                img = self.graph_img.get_image()

                photo_img = ImageTk.PhotoImage(
                    Image.fromarray(img).resize((canvas.winfo_width(), canvas.winfo_height()),
                                                Image.ANTIALIAS))
                canvas.image = photo_img
                canvas.create_image(0, 0, image=photo_img, anchor=NW)
            else:
                self.disable_customisation()
                canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                                   text=f'No image found for the gxl file {gxl_filename}')

    def update_ns_view(self, *args):
        """
        Update node style (color + radius).
        """
        # Update node style color label
        ns_color_label = self.components['ns_color_label']
        ns_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*node_style[self.selected_node.get()]['color'])
        # Update node style radius entry
        ns_entry = self.components['ns_entry']
        ns_entry.delete(0, END)
        ns_entry.insert(0, str(node_style[self.selected_node.get()]['radius']))
        self.onselect()

    def update_ns_radius(self, *args):
        """
        Update the radius of the nodes.
        """
        ns_entry = self.components['ns_entry']
        if ns_entry.get() == '':
            # If user pass no number for the radius -> rewrite previous one
            ns_entry.insert(0, str(node_style[self.selected_node.get()]['radius']))
        else:
            node_style[self.selected_node.get()]['radius'] = int(ns_entry.get())
            self.onselect()

    def update_ns_color(self, *args):
        """
        Update the color of the nodes.
        """
        new_color = colorchooser.askcolor()[0]
        if new_color:
            r, g, b = new_color
            node_style[self.selected_node.get()]['color'] = (r, g, b, 255)
            self.update_ns_view()
            self.onselect()

    def update_es_view(self, *args):
        """
        Update edge style view (color + thickness).
        """
        # Update edge style color label
        es_color_label = self.components['es_color_label']
        es_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*edge_style['color'])
        # Update edge style thickness entry
        es_entry = self.components['es_entry']
        es_entry.delete(0, END)
        es_entry.insert(0, str(edge_style['thickness']))

    def update_es_thickness(self, *args):
        """
        Update the thickness of the edges.
        """
        es_entry = self.components['es_entry']
        if es_entry.get() == '':
            # if user pass no number for thickness -> rewrite previous one
            es_entry.insert(0, str(edge_style['thickness']))
        else:
            edge_style['thickness'] = int(es_entry.get())
            self.onselect()

    def update_es_color(self, *args):
        """
        Update the color of the edges.
        """
        new_color = colorchooser.askcolor()[0]
        if new_color:
            r, g, b = new_color
            edge_style['color'] = (r, g, b, 255)
            self.update_es_view()
            self.onselect()

    def disable_customisation(self):
        """
        Remove the permission to the user to interact with the customisation options.
        """
        for name, customizer in self.customizers.items():
            if customizer:
                component = self.components[name]
                if name in ('ns_color_label', 'es_color_label'):
                    component.unbind('<Button-1>')
                else:
                    component['state'] = DISABLED

    def enable_customisation(self):
        """
        Give the permission to the user to interact with the customisation options.
        """
        for name, customizer in self.customizers.items():
            component = self.components[name]
            if customizer:
                if name == 'ns_color_label':
                    component.bind('<Button-1>', self.update_ns_color)
                elif name == 'es_color_label':
                    component.bind('<Button-1>', self.update_es_color)
                else:
                    component['state'] = NORMAL
