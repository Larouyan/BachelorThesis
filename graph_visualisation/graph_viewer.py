from tkinter import *
from tkinter import colorchooser, filedialog, ttk
from PIL import ImageTk, Image

import os


def select_img_dir():
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            img_dir.set(new_dir)


def select_gxl_dir():
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


def save_img():
    new_dir = filedialog.askdirectory()
    if new_dir:
        if os.path.isdir(new_dir):
            pass


def change_color():
    return colorchooser.askcolor()


def onselect(*args):
    pass
    # todo


if __name__ == '__main__':
    # Create tkinter window
    root = Tk()
    root.title('Graph Viewer')
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.resizable(width=True, height=True)
    root.iconbitmap('diva_banner.ico')
    # root.config(background='#CBCBCB')

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0)
    mainframe.columnconfigure(4, weight=1)
    mainframe.rowconfigure(4, weight=1)
    mainframe.pack(expand=1, fill=BOTH)

    img_dir = StringVar()
    ttk.Button(mainframe, text='Image Path:', command=select_img_dir).grid(column=0, row=0, columnspan=2)
    ttk.Label(mainframe, textvariable=img_dir).grid(column=2, row=0)

    gxl_dir = StringVar()
    ttk.Button(mainframe, text='GXL Path:', command=select_gxl_dir).grid(column=0, row=1, columnspan=2)
    ttk.Label(mainframe, textvariable=gxl_dir).grid(column=2, row=1)

    # Create listbox to list all the gxl files
    listbox = Listbox(mainframe, height=5)
    listbox.grid(column=0, row=2)
    scrollbar = ttk.Scrollbar(mainframe, orient=VERTICAL, command=listbox.yview)
    scrollbar.grid(column=1, row=2)
    listbox['yscrollcommand'] = scrollbar.set
    # listbox.bind('<<ListboxSelect>>', onselect)

    # Canvas to display images
    # canvas_state is True if the canvas is not empty
    canvas_state = BooleanVar()
    canvas_state.set(False)
    canvas = Canvas(mainframe, bg='white')
    canvas.grid(column=2, row=2)

    # Button to save image
    save_button = ttk.Button(mainframe, text='Save As', command=save_img, state=DISABLED)
    save_button.grid(column=0, row=3, columnspan=2)

    # Radio Buttons for color_by_feature
    feature = StringVar()
    feature.set('None')
    # todo

    # Scale for transparency
    transparency = IntVar()
    transparency.set(125)
    transparency_scale = Scale(mainframe, from_=0, to=255, orient=HORIZONTAL, length=255,
                               command=onselect, variable=transparency, state=DISABLED)
    transparency_scale.grid(column=2, row=3)
    # transparency_scale.config(state=ACTIVE)
    
    root.mainloop()
