import tkinter
from tkinter import *
from tkinter import colorchooser, filedialog, ttk

from gui.gui_factory import GUIFactory


class ComponentAlreadyExists(Exception):
    pass


class TkFactory(GUIFactory):
    def __init__(self):
        self.components = dict()
        self.customizers = dict()

    def add_component(self, name: str, widget: tkinter, is_customizer: bool = False):
        if name in self.components:
            print(f'The component {name} has already been added')
            raise ComponentAlreadyExists
        else:
            self.components[name] = widget
            self.customizers[name] = is_customizer

    def create_button(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        button = ttk.Button(frame)
        self.add_component(name, button, is_customizer)
        return button

    def create_label(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        label = ttk.Label(frame)
        self.add_component(name, label, is_customizer)
        return label

    def create_entry(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        entry = ttk.Entry(frame)
        self.add_component(name, entry, is_customizer)
        return entry

    def create_listbox(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        listbox = Listbox(frame)
        self.add_component(name, listbox, is_customizer)
        return listbox

    def create_scrollbar(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        scrollbar = ttk.Scrollbar(frame)
        self.add_component(name, scrollbar, is_customizer)
        return scrollbar

    def create_canvas(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        canvas = Canvas(frame)
        self.add_component(name, canvas, is_customizer)
        return canvas

    def create_checkbutton(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        checkbutton = ttk.Checkbutton(frame)
        self.add_component(name, checkbutton, is_customizer)
        return checkbutton

    def create_scale(self, frame: tkinter.Frame, name: str, is_customizer: bool = False):
        scale = Scale(frame)
        self.add_component(name, scale, is_customizer)
        return scale

    def create_option_menu(self, frame: tkinter.Frame, name: str, is_customizer: bool, value,  *options):
        option_menu = OptionMenu(frame, value, *options)
        self.add_component(name, option_menu, is_customizer)
        return option_menu

    def get_components(self):
        return self.components

    def get_customizers(self):
        return self.customizers
