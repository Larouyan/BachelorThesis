from tkinter import *
from tkinter import colorchooser, filedialog, ttk
from PIL import ImageTk, Image

import os


def select_img_dir(*args):
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            img_dir.set(new_dir)


def select_gxl_dir(*args):
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            load_gxl_dir(new_dir)


def load_gxl_dir(new_dir):
    gxl_dir.set(new_dir)
    # delete previous gxl dir
    listbox.delete(0, END)
    for file in os.listdir(new_dir):
        if file.lower().endswith('.gxl'):
            if os.path.isfile(os.path.join(new_dir, file)):
                listbox.insert(END, file.rsplit('.', 1)[0])
    listbox.select_set(0)
    # onselect()


def save_img(*args):
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            pass


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


def update_ns_view(*args):
    # Update node style color label
    ns_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*node_style[selected_node.get()]['color'])
    # Update node style radius entry
    ns_entry.delete(0, END)
    ns_entry.insert(0, str(node_style[selected_node.get()]['radius']))


def update_ns_radius(*args):
    if ns_entry.get() == '':
        # If user pass no number for the radius -> rewrite previous one
        ns_entry.insert(0, str(node_style[selected_node.get()]['radius']))
    else:
        node_style[selected_node.get()]['radius'] = int(ns_entry.get())
        onselect()


def update_ns_color(*args):
    new_color = colorchooser.askcolor()[0]
    if new_color:
        node_style[selected_node.get()]['color'] = new_color
        update_ns_view()
        onselect()


def update_es_view(*args):
    # Update edge style color label
    es_color_label['background'] = '#{:02x}{:02x}{:02x}'.format(*edge_style['color'])
    # Update edge style thickness entry
    es_entry.delete(0, END)
    es_entry.insert(0, str(edge_style['thickness']))


def update_es_thickness(*args):
    if es_entry.get() == '':
        # if user pass no number for thickness -> rewrite previous one
        es_entry.insert(0, str(edge_style['thickness']))
    else:
        edge_style['thickness'] = int(es_entry.get())
        onselect()


def update_es_color(*args):
    new_color = colorchooser.askcolor()[0]
    if new_color:
        edge_style['color'] = new_color
        update_es_view()
        onselect()


def onselect(*args):
    print('onselect')
    pass
    # todo: display image with graph on canvas


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
    mainframe.columnconfigure(4, weight=1)
    mainframe.rowconfigure(4, weight=1)
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
    lbf = Frame(mainframe)
    lbf.grid(column=0, row=2, columnspan=2)
    listbox = Listbox(lbf, height=10)
    listbox.pack(side=LEFT, fill=BOTH)
    scrollbar = ttk.Scrollbar(lbf, orient=VERTICAL, command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    listbox['yscrollcommand'] = scrollbar.set
    listbox.bind('<<ListboxSelect>>', onselect)

    # Canvas to display images
    # canvas_state is True if the canvas is not empty
    canvas_state = BooleanVar()
    canvas_state.set(False)
    canvas = Canvas(mainframe, bg='white')
    canvas.grid(column=2, row=2, rowspan=6, columnspan=2)

    # Button to save image
    save_button = ttk.Button(mainframe, text='Save As', command=save_img, state=DISABLED)
    save_button.grid(column=0, row=3, columnspan=2)

    # Scale for transparency
    transparency = IntVar()
    transparency.set(125)
    transparency_scale = Scale(mainframe, from_=0, to=255, orient=HORIZONTAL, length=255, activebackground='red',
                               command=onselect, variable=transparency, state=DISABLED)
    transparency_scale.grid(column=2, row=8, columnspan=2)
    # transparency_scale.config(state=ACTIVE)

    # Radio Buttons for color_by_feature
    feature = StringVar()
    feature.set('None')
    # todo: color_by_feature

    # Scaling
    scaling = StringVar()
    scaling.set('1.0')
    ttk.Label(mainframe, text='Scaling: ').grid(column=2, row=9)
    # register function to check if the entry is a float number or not
    reg = mainframe.register(is_number)
    scaling_entry = Entry(mainframe, textvariable=scaling, validate='key', validatecommand=(reg, '%P'), state=DISABLED)
    scaling_entry.bind('<Return>', onselect)
    scaling_entry.grid(column=3, row=9)

    # Node Style
    nodes = ['tumorbud', 'lymphocyte']
    node_style = {'tumorbud': {'color': (175, 230, 25, 255), 'radius': 22},
                  'lymphocyte': {'color': (255, 45, 240, 255), 'radius': 15},
                  'thickness': -1}

    ttk.Label(mainframe, text='Node Style').grid(column=4, row=2)

    selected_node = StringVar()
    selected_node.set(nodes[0])
    ns_option_menu = OptionMenu(mainframe, selected_node, *nodes, command=update_ns_view)
    ns_option_menu.grid(column=4, row=3)

    ttk.Label(mainframe, text='Node Color').grid(column=4, row=4)
    ns_color_label = ttk.Label(mainframe, width=10)
    ns_color_label.grid(column=4, row=5)
    ns_color_label.bind('<Button-1>', update_ns_color)

    ttk.Label(mainframe, text='Node Radius').grid(column=4, row=6)
    # register function to check if the entry is a float number or not
    reg_is_int = mainframe.register(is_int)
    ns_entry = Entry(mainframe, validate='key', validatecommand=(reg_is_int, '%P'))
    ns_entry.grid(column=4, row=7)
    ns_entry.bind('<Return>', update_ns_radius)

    # Edge Style
    edge_style = {'color': (168, 50, 117, 255), 'thickness': 5}

    ttk.Label(mainframe, text='Edge Style').grid(column=5, row=2)

    ttk.Label(mainframe, text='Edge Color').grid(column=5, row=4)
    es_color_label = ttk.Label(mainframe, width=10)
    es_color_label.grid(column=5, row=5)
    es_color_label.bind('<Button-1>', update_es_color)

    ttk.Label(mainframe, text='Edge Thickness').grid(column=5, row=6)
    es_entry = Entry(mainframe, validate='key', validatecommand=(reg_is_int, '%P'))
    es_entry.grid(column=5, row=7)
    es_entry.bind('<Return>', update_es_thickness)

    update_ns_view()
    update_es_view()
    root.mainloop()
