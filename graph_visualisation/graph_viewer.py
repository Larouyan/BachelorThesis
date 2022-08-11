from tkinter import *
from tkinter import colorchooser, filedialog, ttk
from PIL import ImageTk, Image

from graph_plotter import graph_plotter
from util.draw_graph import GraphDrawer
from util.default_config import node_style, edge_style, nodes
from util.gxl_graph import ParsedGxlGraph

import os
import re

graph_img = GraphDrawer


def select_img_dir(*args):
    """
    Ask the user for the directory where the images are.
    :param args:
    :return:
    """
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            img_dir.set(new_dir)


def select_gxl_dir(*args):
    """
    Ask user for the directory where the gxl files are.
    :param args:
    :return:
    """
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            load_gxl_dir(new_dir)


def load_gxl_dir(new_dir):
    """
    Load the gxl files on the listbox.
    :param new_dir: directory where the gxl files are.
    :return:
    """
    gxl_dir.set(new_dir)
    # delete previous gxl dir
    listbox.delete(0, END)
    for file in os.listdir(new_dir):
        if file.lower().endswith('.gxl'):
            if os.path.isfile(os.path.join(new_dir, file)):
                listbox.insert(END, file.rsplit('.', 1)[0])
    if listbox.size() > 0:
        listbox.select_set(0)
        create_cbf_menu()
        onselect()


def save_img(*args):
    """
    Save the current image
    :param args:
    :return:
    """
    output_path = filedialog.askdirectory()
    if output_path:
        if os.path.isdir(output_path):
            graph_img.save(output_path)


def save_all(*arg):
    """
    Save all images with graph in a directory chosen by the user.
    :param arg:
    :return:
    """
    output_path = filedialog.askdirectory()
    if output_path:
        if os.path.isdir(output_path):
            for gxl_file in os.listdir(gxl_dir.get()):
                gxl_filename = gxl_file.rsplit('.', 1)[0]
                img_filepath = search_img_filepath(gxl_filename)
                if img_filepath:
                    gxl_filepath = os.path.join(gxl_dir.get(), gxl_file)
                    temp_graph = graph_plotter(gxl_filepath=gxl_filepath, img_filepath=img_filepath,
                                               color_by_feature=get_color_by_feature(),
                                               node_style=node_style, edge_style=edge_style,
                                               scaling=float(scaling.get()), transparency=transparency.get(),
                                               current_node=selected_node.get())
                    temp_graph.save(output_path)


def is_number(inp):
    if inp == '':
        return True
    try:
        float(inp)
        return True
    except ValueError:
        return False


def is_int(inp):
    if inp == '':
        return True
    try:
        int(inp)
        return True
    except ValueError:
        return False


def create_cbf_menu():
    get_features()
    pass


def update_ns_view(*args):
    """
    Update node style (color + radius)
    :param args:
    :return:
    """
    # Update node style color label
    ns_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*node_style[selected_node.get()]['color'])
    # Update node style radius entry
    ns_entry.delete(0, END)
    ns_entry.insert(0, str(node_style[selected_node.get()]['radius']))
    onselect()


def update_ns_radius(*args):
    """
    update the radius of the nodes
    :param args:
    :return:
    """
    if ns_entry.get() == '':
        # If user pass no number for the radius -> rewrite previous one
        ns_entry.insert(0, str(node_style[selected_node.get()]['radius']))
    else:
        node_style[selected_node.get()]['radius'] = int(ns_entry.get())
        onselect()


def update_ns_color(*args):
    """
    update the color of the nodes
    :param args:
    :return:
    """
    new_color = colorchooser.askcolor()[0]
    if new_color:
        r, g, b = new_color
        node_style[selected_node.get()]['color'] = (r, g, b, 255)
        update_ns_view()
        onselect()


def update_es_view(*args):
    """
    update edge style view (color + thickness)
    :param args:
    :return:
    """
    # Update edge style color label
    es_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*edge_style['color'])
    # Update edge style thickness entry
    es_entry.delete(0, END)
    es_entry.insert(0, str(edge_style['thickness']))


def update_es_thickness(*args):
    """
    update the thickness of the edges
    :param args:
    :return:
    """
    if es_entry.get() == '':
        # if user pass no number for thickness -> rewrite previous one
        es_entry.insert(0, str(edge_style['thickness']))
    else:
        edge_style['thickness'] = int(es_entry.get())
        onselect()


def update_es_color(*args):
    """
    update the color of the edges
    :param args:
    :return:
    """
    new_color = colorchooser.askcolor()[0]
    if new_color:
        r, g, b = new_color
        edge_style['color'] = (r, g, b, 255)
        update_es_view()
        onselect()


def disable_customisation():
    """
    Disable the customisation options for the user
    :return:
    """
    save_button['state'], save_all_button['state'] = DISABLED, DISABLED
    for child in bottom_canvas_frame.winfo_children() + right_canvas_frame.winfo_children():
        child['state'] = DISABLED
        if child is ns_color_label or es_color_label:
            child.unbind('<Button-1>')


def enable_customisation():
    """
    Allow user to interact with the customisation options
    :return:
    """
    save_button['state'], save_all_button['state'] = NORMAL, NORMAL
    for child in bottom_canvas_frame.winfo_children() + right_canvas_frame.winfo_children():
        child['state'] = NORMAL
        if child is ns_color_label:
            child.bind('<Button-1>', update_ns_color)
        elif child is es_color_label:
            child.bind('<Button-1>', update_es_color)


def get_color_by_feature():
    """
    :return: Selected feature
    """
    if color_by_feature.get() == 'None':
        return None
    else:
        return color_by_feature.get()


def get_features():
    """
    Fill the option menu with the nodes features.
    :return:
    """
    parsed = ParsedGxlGraph(os.path.join(gxl_dir.get(), os.listdir(gxl_dir.get())[0]))
    features = [f for f in parsed.node_feature_names if f not in ['x', 'y']]
    for feature in features:
        cbf_menu['menu'].add_command(label=feature, command=lambda value=feature: color_by_feature.set(value))


def onselect(*args):
    """
    Draw the image with the graph on the canvas
    :param args:
    :return:
    """
    global graph_img
    if img_dir.get() != '':
        canvas.delete("all")
        try:
            index = int(listbox.curselection()[0])
            gxl_filename = listbox.get(index)
        except IndexError:
            # If listbox is unselected then take the previous gxl file which was selected
            gxl_filename = graph_img.graph.file_id

        gxl_filepath = os.path.join(gxl_dir.get(), gxl_filename + '.gxl')
        img_filepath = search_img_filepath(gxl_filename)
        if img_filepath:
            if os.path.isfile(img_filepath) and os.path.isfile(gxl_filepath):
                enable_customisation()

                graph_img = graph_plotter(gxl_filepath=gxl_filepath, img_filepath=img_filepath,
                                          color_by_feature=get_color_by_feature(),
                                          node_style=node_style, edge_style=edge_style,
                                          scaling=float(scaling.get()), transparency=transparency.get(),
                                          current_node=selected_node.get())
                img = graph_img.get_image()

                photo_img = ImageTk.PhotoImage(Image.fromarray(img).resize((canvas.winfo_width(), canvas.winfo_height()),
                                                                           Image.ANTIALIAS))
                canvas.image = photo_img
                canvas.create_image(0, 0, image=photo_img, anchor=NW)
        else:
            disable_customisation()
            canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                               text=f'No image found for the gxl file {gxl_filename}')


def search_img_filepath(gxl_filename):
    """
    Find the image corresponding to the gxl file given in input
    :param gxl_filename: name of the gxl file.
    :return:
    """
    extensions = ('png', 'bmp', 'jpg', 'jpeg', 'gif')

    for img in os.listdir(img_dir.get()):
        if re.match(r'.*' + re.escape(gxl_filename) + r'.*', img):
            for ext in extensions:
                if img.endswith(ext):
                    return os.path.join(img_dir.get(), img)

    return None


if __name__ == '__main__':
    # Create tkinter window
    root = Tk()
    root.title('Graph Viewer')
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.resizable(width=True, height=True)
    root.iconbitmap('diva_banner.ico')
    # root.config(background='#CBCBCB')

    # Create main frame where element are displayed
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0)
    mainframe.columnconfigure(10, weight=1)
    mainframe.rowconfigure(10, weight=1)
    mainframe.pack(expand=1, fill=BOTH)

    # Create button asking user to give the path of folder containing hotspot images
    img_dir = StringVar()
    ttk.Button(mainframe, text='Image Path:', command=select_img_dir).grid(column=0, row=0, columnspan=2)
    ttk.Label(mainframe, textvariable=img_dir).grid(column=2, row=0)

    # Create button asking user to give the path of folder containing gxl files
    gxl_dir = StringVar()
    ttk.Button(mainframe, text='GXL Path:', command=select_gxl_dir).grid(column=0, row=1, columnspan=2)
    ttk.Label(mainframe, textvariable=gxl_dir).grid(column=2, row=1)

    # Create listbox to list all the gxl files
    lbf = ttk.Frame(mainframe)
    lbf.grid(column=0, row=2, columnspan=2)
    listbox = Listbox(lbf, height=15)
    listbox.pack(side=LEFT, fill=BOTH)
    scrollbar = ttk.Scrollbar(lbf, orient=VERTICAL, command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    listbox['yscrollcommand'] = scrollbar.set
    listbox.bind('<<ListboxSelect>>', onselect)

    # Canvas to display images
    canvas = Canvas(mainframe, width=512, height=512, bg='white')
    canvas.grid(column=2, row=2, rowspan=6, columnspan=2)

    # Button to save current image
    save_button = ttk.Button(mainframe, text='Save As', command=save_img)
    save_button.grid(column=0, row=10, columnspan=2)

    # Button to save all images
    save_all_button = ttk.Button(mainframe, text='Save All', command=save_all)
    save_all_button.grid(column=0, row=11, columnspan=2)

    # Customisation on the left of the canvas
    bottom_canvas_frame = Frame(mainframe)
    bottom_canvas_frame.grid(column=2, row=9, columnspan=2, rowspan=5)

    # Transparency
    transparency = IntVar()
    transparency.set(125)
    transparency_scale = Scale(bottom_canvas_frame, from_=0, to=255, orient=HORIZONTAL, length=255,
                               activebackground='red', command=onselect, variable=transparency)
    transparency_scale.grid(column=0, row=0, columnspan=2)

    # Scaling
    scaling = StringVar()
    scaling.set('1.0')
    ttk.Label(bottom_canvas_frame, text='Scaling: ').grid(column=0, row=1)
    # register function to check if the entry is a float number or not
    reg_is_number = mainframe.register(is_number)
    scaling_entry = Entry(bottom_canvas_frame, textvariable=scaling, validate='key',
                          validatecommand=(reg_is_number, '%P'))
    scaling_entry.grid(column=1, row=1)
    scaling_entry.bind('<Return>', onselect)

    # Color_by_feature
    color_by_feature = StringVar()
    color_by_feature.set('None')
    color_by_feature.trace('w', onselect)

    ttk.Label(bottom_canvas_frame, text='Color by feature:').grid(column=0, row=3)
    cbf_menu = OptionMenu(bottom_canvas_frame, color_by_feature, color_by_feature.get())
    cbf_menu.grid(column=1, row=3)

    # Customisation on the right of the canvas
    right_canvas_frame = ttk.Frame(mainframe)
    right_canvas_frame.grid(column=4, row=2, columnspan=2, rowspan=6)

    # Node Style
    ttk.Label(right_canvas_frame, text='Node Style', font=('Times', 18, 'bold')).grid(column=0, row=0)

    selected_node = StringVar()
    selected_node.set(nodes[0])
    ns_option_menu = OptionMenu(right_canvas_frame, selected_node, *nodes, command=update_ns_view)
    ns_option_menu.grid(column=0, row=1)

    ttk.Label(right_canvas_frame, text='Node Color').grid(column=0, row=2)
    ns_color_label = ttk.Label(right_canvas_frame, width=10)
    ns_color_label.grid(column=0, row=3)
    ns_color_label.bind('<Button-1>', update_ns_color)

    ttk.Label(right_canvas_frame, text='Node Radius').grid(column=0, row=4)
    # register function to check if the entry is a float number or not
    reg_is_int = mainframe.register(is_int)
    ns_entry = Entry(right_canvas_frame, validate='key', validatecommand=(reg_is_int, '%P'))
    ns_entry.grid(column=0, row=5)
    ns_entry.bind('<Return>', update_ns_radius)

    # Edge Style
    ttk.Label(right_canvas_frame, text='Edge Style', font=('Times', 18, 'bold')).grid(column=1, row=0)

    ttk.Label(right_canvas_frame, text='Edge Color').grid(column=1, row=2)
    es_color_label = ttk.Label(right_canvas_frame, width=10)
    es_color_label.grid(column=1, row=3)
    es_color_label.bind('<Button-1>', update_es_color)

    ttk.Label(right_canvas_frame, text='Edge Thickness').grid(column=1, row=4)
    es_entry = Entry(right_canvas_frame, validate='key', validatecommand=(reg_is_int, '%P'))
    es_entry.grid(column=1, row=5)
    es_entry.bind('<Return>', update_es_thickness)

    update_ns_view()
    update_es_view()
    # disable customisation when there is no picture on the canvas
    disable_customisation()

    root.mainloop()
