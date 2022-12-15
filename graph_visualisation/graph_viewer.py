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
listbox_content = []


def select_img_dir(*args):
    """
    Ask the user for the directory where the images are.
    """
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            img_dir.set(new_dir)


def select_gxl_dir(*args):
    """
    Ask the user for the directory where the gxl files are.
    """
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            load_gxl_dir(new_dir)


def load_gxl_dir(new_dir):
    """
    Load the gxl files on the listbox.
    :param new_dir: directory where the gxl files are.
    """
    global listbox_content
    gxl_dir.set(new_dir)
    # delete previous gxl dir
    listbox.delete(0, END)
    for file in sorted(os.listdir(new_dir)):
        if file.lower().endswith('.gxl'):
            if os.path.isfile(os.path.join(new_dir, file)):
                listbox.insert(END, file.rsplit('.', 1)[0])
    if listbox.size() > 0:
        listbox.select_set(0)
        listbox_content = listbox.get(0, END)
        lb_entry['state'] = NORMAL
        create_cbf_menu()
        onselect()


def update_gxl_listbox(pattern):
    """
    Update the list of gxl files such that it only display files that start with a given pattern.
    :param pattern: string given by the user.
    """
    listbox.delete(0, END)
    for file in listbox_content:
        if str(file).upper().startswith(pattern.get().upper()):
            listbox.insert(END, file)


def save_img(*args):
    """
    Save the current image in a directory chosen by the user.
    """
    output_path = filedialog.askdirectory()
    if output_path:
        if os.path.isdir(output_path):
            graph_img.save(output_path)


def save_all(*arg):
    """
    Save all images in a directory chosen by the user.
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
    Update node style (color + radius).
    """
    # Update node style color label
    ns_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*node_style[selected_node.get()]['color'])
    # Update node style radius entry
    ns_entry.delete(0, END)
    ns_entry.insert(0, str(node_style[selected_node.get()]['radius']))
    onselect()


def update_ns_radius(*args):
    """
    Update the radius of the nodes.
    """
    if ns_entry.get() == '':
        # If user pass no number for the radius -> rewrite previous one
        ns_entry.insert(0, str(node_style[selected_node.get()]['radius']))
    else:
        node_style[selected_node.get()]['radius'] = int(ns_entry.get())
        onselect()


def update_ns_color(*args):
    """
    Update the color of the nodes.
    """
    new_color = colorchooser.askcolor()[0]
    if new_color:
        r, g, b = new_color
        node_style[selected_node.get()]['color'] = (r, g, b, 255)
        update_ns_view()
        onselect()


def update_es_view(*args):
    """
    Update edge style view (color + thickness).
    """
    # Update edge style color label
    es_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*edge_style['color'])
    # Update edge style thickness entry
    es_entry.delete(0, END)
    es_entry.insert(0, str(edge_style['thickness']))


def update_es_thickness(*args):
    """
    Update the thickness of the edges.
    """
    if es_entry.get() == '':
        # if user pass no number for thickness -> rewrite previous one
        es_entry.insert(0, str(edge_style['thickness']))
    else:
        edge_style['thickness'] = int(es_entry.get())
        onselect()


def update_es_color(*args):
    """
    Update the color of the edges.
    """
    new_color = colorchooser.askcolor()[0]
    if new_color:
        r, g, b = new_color
        edge_style['color'] = (r, g, b, 255)
        update_es_view()
        onselect()


def disable_customisation():
    """
    Remove the permission to the user to interact with the customisation options.
    """
    save_button['state'], save_all_button['state'], lb_entry['state'] = DISABLED, DISABLED, DISABLED
    for child in right_canvas_frame.winfo_children():
        if child not in (blank_checkbutton, blank_label):
            child['state'] = DISABLED
        if child is ns_color_label or es_color_label:
            child.unbind('<Button-1>')


def enable_customisation():
    """
    Give the permission to the user to interact with the customisation options.
    """
    save_button['state'], save_all_button['state'] = NORMAL, NORMAL
    for child in right_canvas_frame.winfo_children():
        child['state'] = NORMAL
        if child is ns_color_label:
            child.bind('<Button-1>', update_ns_color)
        elif child is es_color_label:
            child.bind('<Button-1>', update_es_color)


def get_color_by_feature():
    """
    :return: Selected feature.
    """
    if color_by_feature.get() == 'None':
        return None
    else:
        return color_by_feature.get()


def get_features():
    """
    Fill the option menu with the nodes features.
    """
    parsed = ParsedGxlGraph(os.path.join(gxl_dir.get(), os.listdir(gxl_dir.get())[0]))
    features = [f for f in parsed.node_feature_names if f not in ['x', 'y']]
    for feature in features:
        cbf_menu['menu'].add_command(label=feature, command=lambda value=feature: color_by_feature.set(value))


def onselect(*args):
    """
    Draw the image with the graph on the canvas
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

        if img_filepath or (not img_filepath and cb_blank.get()):
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
    Find the image corresponding to the gxl file given in input.
    :param gxl_filename: name of the gxl file.
    :return: The path to the corresponding image if it exists, otherwise it returns None.
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
    for col in range(10):
        mainframe.columnconfigure(col, weight=1)
        for row in range(10):
            mainframe.rowconfigure(row, weight=1)

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
    lbf.grid(column=0, row=4, columnspan=2)
    listbox = Listbox(lbf, height=15)
    listbox.pack(side=LEFT, fill=BOTH)
    scrollbar = ttk.Scrollbar(lbf, orient=VERTICAL, command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    listbox['yscrollcommand'] = scrollbar.set
    listbox.bind('<<ListboxSelect>>', onselect)

    ttk.Label(mainframe, text='Search').grid(column=0, row=2, columnspan=2, rowspan=2)

    lb_pattern = StringVar()
    lb_pattern.trace("w", lambda name, index, mode, lb_pattern=lb_pattern: update_gxl_listbox(lb_pattern))
    lb_entry = Entry(mainframe, textvariable=lb_pattern)
    lb_entry.grid(column=0, row=3, columnspan=2)

    # Canvas to display images
    canvas = Canvas(mainframe, width=600, height=600, bg='white')
    canvas.grid(column=2, row=2, rowspan=6, columnspan=2, sticky='nsew')

    # Button to save current image
    save_button = ttk.Button(mainframe, text='Save As', command=save_img)
    save_button.grid(column=0, row=10, columnspan=2)

    # Button to save all images
    save_all_button = ttk.Button(mainframe, text='Save All', command=save_all)
    save_all_button.grid(column=0, row=11, columnspan=2)

    # Customisation on the right of the canvas
    right_canvas_frame = ttk.Frame(mainframe)
    right_canvas_frame.grid(column=6, row=2, columnspan=2, rowspan=12)

    # Transparency
    ttk.Label(right_canvas_frame, text='Transparency').grid(column=0, row=6, columnspan=2)
    transparency = IntVar()
    transparency.set(125)
    transparency_scale = Scale(right_canvas_frame, from_=0, to=255, orient=HORIZONTAL, length=255,
                               activebackground='red', command=onselect, variable=transparency)
    transparency_scale.grid(column=0, row=7, columnspan=2)

    # Scaling
    scaling = StringVar()
    scaling.set('1.0')
    ttk.Label(right_canvas_frame, text='Scaling: ').grid(column=0, row=8)
    # Good scaling for hotspot images = 4.118660172440437

    # register function to check if the entry is a float number or not
    reg_is_number = mainframe.register(is_number)
    scaling_entry = Entry(right_canvas_frame, textvariable=scaling, validate='key',
                          validatecommand=(reg_is_number, '%P'))
    scaling_entry.grid(column=1, row=8)
    scaling_entry.bind('<Return>', onselect)

    # Color_by_feature
    color_by_feature = StringVar()
    color_by_feature.set('None')
    color_by_feature.trace('w', onselect)

    ttk.Label(right_canvas_frame, text='Color by feature:').grid(column=0, row=10)
    cbf_menu = OptionMenu(right_canvas_frame, color_by_feature, color_by_feature.get())
    cbf_menu.grid(column=1, row=10)

    # Checkbutton if the background should be blank when a graph didn't match with any images
    cb_blank = BooleanVar()
    cb_blank.set(False)

    blank_checkbutton = ttk.Checkbutton(right_canvas_frame, command=onselect, offvalue=False, onvalue=True,
                                        variable=cb_blank)
    blank_checkbutton.grid(column=1, row=11)
    blank_label = ttk.Label(right_canvas_frame, text='Blank background ?')
    blank_label.grid(column=0, row=11)

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

    for row in range(11):
        right_canvas_frame.rowconfigure(row, weight=1)
    for col in range(2):
        right_canvas_frame.columnconfigure(col, weight=1)

    update_ns_view()
    update_es_view()
    # disable customisation when there is no picture on the canvas
    disable_customisation()

    root.mainloop()
