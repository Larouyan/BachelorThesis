
from tkinter import *
from tkinter import ttk

from util.default_config import nodes

from gui.tk_factory import TkFactory

from graph_viewer import GraphViewer


def is_int(inp):
    if inp == '':
        return True
    try:
        int(inp)
        return True
    except ValueError:
        return False


def is_number(inp):
    if inp == '':
        return True
    try:
        float(inp)
        return True
    except ValueError:
        return False


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

    # Variables:
    # images directory
    img_dir = StringVar()
    # gxl files directory
    gxl_dir = StringVar()
    # feature in which the nodes are colored
    color_by_feature = StringVar()
    color_by_feature.set('None')
    # decide if there is no image corresponding to a gxl file -> True: Draw graph on blank background / False: Empty
    cb_blank = BooleanVar()
    cb_blank.set(False)
    # Transparency
    transparency = IntVar()
    transparency.set(125)
    # Scaling
    scaling = StringVar()
    scaling.set('1.0')
    # Type of node selected in the option menu of the node style
    selected_node = StringVar()
    selected_node.set(nodes[0])

    graph_viewer = GraphViewer(img_dir, gxl_dir, color_by_feature, cb_blank, transparency, scaling, selected_node)
    tk_factory = TkFactory()

    # Create button asking user to give the path of folder containing hotspot images
    img_path_button = tk_factory.create_button(mainframe, 'img_path_button')
    img_path_button.grid(column=0, row=0, columnspan=2)
    img_path_button.configure(text='Image Path:', command=graph_viewer.select_img_dir)

    img_path_label = tk_factory.create_label(mainframe, 'img_path_label')
    img_path_label.grid(column=2, row=0)
    img_path_label.configure(textvariable=graph_viewer.img_dir)

    # Create button asking user to give the path of folder containing gxl files
    gxl_path_button = tk_factory.create_button(mainframe, 'gxl_path_button')
    gxl_path_button.grid(column=0, row=1, columnspan=2)
    gxl_path_button.configure(text='GXL Path:', command=graph_viewer.select_gxl_dir)

    gxl_path_label = tk_factory.create_label(mainframe, 'gxl_path_label')
    gxl_path_label.grid(column=2, row=1)
    gxl_path_label.configure(textvariable=graph_viewer.gxl_dir)

    # Create listbox to list all the gxl files
    lbf = ttk.Frame(mainframe)
    lbf.grid(column=0, row=4, columnspan=2)

    listbox = tk_factory.create_listbox(lbf, 'gxl_listbox')
    listbox.configure(height=15)
    listbox.pack(side=LEFT, fill=BOTH)

    scrollbar = tk_factory.create_scrollbar(lbf, 'gxl_scrollbar')
    scrollbar.configure(orient=VERTICAL, command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    listbox['yscrollcommand'] = scrollbar.set
    listbox.bind('<<ListboxSelect>>', graph_viewer.onselect)

    gxl_search_label = tk_factory.create_label(mainframe, 'gxl_search_label')
    gxl_search_label.grid(column=0, row=2, columnspan=2, rowspan=2)
    gxl_search_label.configure(text='Search')

    lb_pattern = StringVar()
    lb_pattern.trace("w", lambda name, index, mode, lb_pattern=lb_pattern: graph_viewer.update_gxl_listbox(lb_pattern))

    lb_entry = tk_factory.create_entry(mainframe, 'lb_entry')
    lb_entry.configure(textvariable=lb_pattern, state=DISABLED)
    lb_entry.grid(column=0, row=3, columnspan=2)

    # Canvas to display images
    canvas = tk_factory.create_canvas(mainframe, 'canvas')
    canvas.configure(width=600, height=600, bg='white')
    # canvas = Canvas(mainframe, width=600, height=600, bg='white')
    canvas.grid(column=2, row=2, rowspan=6, columnspan=2, sticky='nsew')

    # Button to save current image
    save_button = tk_factory.create_button(mainframe, 'save_button', True)
    save_button.configure(text='Save As', command=graph_viewer.save_img)
    save_button.grid(column=0, row=10, columnspan=2)

    # Button to save all images
    save_all_button = tk_factory.create_button(mainframe, 'save_all_button', True)
    save_all_button.configure(text='Save All', command=graph_viewer.save_all)
    save_all_button.grid(column=0, row=11, columnspan=2)

    # Customisation on the right of the canvas
    right_canvas_frame = ttk.Frame(mainframe)
    right_canvas_frame.grid(column=6, row=2, columnspan=2, rowspan=12)

    # Transparency
    transparency_label = tk_factory.create_label(right_canvas_frame, 'transparency_label', True)
    transparency_label.grid(column=0, row=6, columnspan=2)
    transparency_label.configure(text='Transparency')

    transparency_scale = tk_factory.create_scale(right_canvas_frame, 'transparency_scale', True)
    transparency_scale.configure(from_=0, to=255, orient=HORIZONTAL, length=255,
                                 activebackground='red', command=graph_viewer.onselect, variable=transparency)
    transparency_scale.grid(column=0, row=7, columnspan=2)

    # Scaling
    scaling_label = tk_factory.create_label(right_canvas_frame, 'scaling_label', True)
    scaling_label.grid(column=0, row=8)
    scaling_label.configure(text='Scaling: ')
    # Good scaling for hotspot images = 4.118660172440437

    # register function to check if the entry is a float number or not
    reg_is_number = mainframe.register(is_number)

    scaling_entry = tk_factory.create_entry(right_canvas_frame, 'scaling_entry', True)
    scaling_entry.configure(textvariable=scaling, validate='key', validatecommand=(reg_is_number, '%P'))
    scaling_entry.grid(column=1, row=8)
    scaling_entry.bind('<Return>', graph_viewer.onselect)

    # Color_by_feature
    color_by_feature.trace('w', graph_viewer.onselect)

    cbf_label = tk_factory.create_label(right_canvas_frame, 'cbf_label', True)
    cbf_label.configure(text='Color by feature:')
    cbf_label.grid(column=0, row=10)

    # ttk.Label(right_canvas_frame, text='Color by feature:').grid(column=0, row=10)
    # cbf_menu = OptionMenu(right_canvas_frame, color_by_feature, color_by_feature.get())
    cbf_menu = tk_factory.create_option_menu(right_canvas_frame, 'cbf_menu', True,
                                             color_by_feature, color_by_feature.get())
    cbf_menu.grid(column=1, row=10)

    # Checkbutton if the background should be blank when a graph didn't match with any images
    blank_checkbutton = tk_factory.create_checkbutton(right_canvas_frame, 'blank_checkbutton')
    blank_checkbutton.configure(command=graph_viewer.onselect, offvalue=False, onvalue=True, variable=cb_blank)
    blank_checkbutton.grid(column=1, row=11)
    blank_label = tk_factory.create_label(right_canvas_frame, 'blank_label')
    blank_label.configure(text='Blank background ?')
    blank_label.grid(column=0, row=11)

    # Node Style
    ns_label = tk_factory.create_label(right_canvas_frame, 'ns_label', True)
    ns_label.configure(text='Node Style', font=('Times', 18, 'bold'))
    ns_label.grid(column=0, row=0)

    selected_node.trace('w', graph_viewer.update_ns_view)
    ns_option_menu = tk_factory.create_option_menu(right_canvas_frame, 'ns_option_menu', True, selected_node, *nodes)
    ns_option_menu.grid(column=0, row=1)

    node_color_label = tk_factory.create_label(right_canvas_frame, 'node_color_label', True)
    node_color_label.configure(text='Node Color')
    node_color_label.grid(column=0, row=2)
    ns_color_label = tk_factory.create_label(right_canvas_frame, 'ns_color_label', True)
    ns_color_label.configure(width=15)
    ns_color_label.grid(column=0, row=3)
    ns_color_label.bind('<Button-1>', graph_viewer.update_ns_color)

    # ttk.Label(right_canvas_frame, ).grid(column=0, row=4)
    node_radius_label = tk_factory.create_label(right_canvas_frame, 'node_radius_label', True)
    node_radius_label.configure(text='Node Radius')
    node_radius_label.grid(column=0, row=4)
    # register function to check if the entry is a float number or not
    reg_is_int = mainframe.register(is_int)
    ns_entry = tk_factory.create_entry(right_canvas_frame, 'ns_entry', True)
    ns_entry.configure(validate='key', validatecommand=(reg_is_int, '%P'))
    ns_entry.grid(column=0, row=5)
    ns_entry.bind('<Return>', graph_viewer.update_ns_radius)

    # Edge Style
    es_label = tk_factory.create_label(right_canvas_frame, 'es_label', True)
    es_label.configure(text='Edge Style', font=('Times', 18, 'bold'))
    es_label.grid(column=1, row=0)
    # ttk.Label(right_canvas_frame, ).grid(column=1, row=0)

    edge_color_label = tk_factory.create_label(right_canvas_frame, 'edge_color_label', True)
    edge_color_label.configure(text='Edge Color')
    edge_color_label.grid(column=1, row=2)

    es_color_label = tk_factory.create_label(right_canvas_frame, 'es_color_label', True)
    es_color_label.configure(width=15)
    es_color_label.grid(column=1, row=3)
    es_color_label.bind('<Button-1>', graph_viewer.update_es_color)

    edge_thickness = tk_factory.create_label(right_canvas_frame, 'edge_thickness', True)
    edge_thickness.configure(text='Edge Thickness')
    edge_thickness.grid(column=1, row=4)
    es_entry = tk_factory.create_entry(right_canvas_frame, 'es_entry', True)
    es_entry.configure(validate='key', validatecommand=(reg_is_int, '%P'))
    es_entry.grid(column=1, row=5)
    es_entry.bind('<Return>', graph_viewer.update_es_thickness)

    graph_viewer.set_components_customizers(tk_factory)

    for row in range(11):
        right_canvas_frame.rowconfigure(row, weight=1)
    for col in range(2):
        right_canvas_frame.columnconfigure(col, weight=1)

    graph_viewer.update_ns_view()
    graph_viewer.update_es_view()
    # disable customisation when there is no picture on the canvas
    graph_viewer.disable_customisation()

    root.mainloop()
