from tkinter import filedialog, messagebox

def select_folder():
    return filedialog.askdirectory()

def show_error(title, message):
    messagebox.showerror(title, message)

def show_info(title, message):
    messagebox.showinfo(title, message)