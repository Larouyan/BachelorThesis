from tkinter import *
from tkinter import colorchooser
from tkinter import ttk


def change_color():
    return colorchooser.askcolor()


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
    mainframe.columnconfigure(2, weight=1)
    mainframe.rowconfigure(2, weight=1)
    mainframe.pack(expand=1, fill='both')

    

    root.mainloop()
