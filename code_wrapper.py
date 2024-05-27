import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Define selected_subfolders as a global variable
selected_subfolders = []


def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(tk.END, folder_path)
    if folder_path:
        select_subfolders(folder_path)


def select_subfolders(folder_path):
    subfolders = [dir for dir in os.listdir(
        folder_path) if os.path.isdir(os.path.join(folder_path, dir))]

    subfolder_window = tk.Toplevel(window)
    subfolder_window.title("Select Subfolders")

    subfolder_listbox = tk.Listbox(subfolder_window, selectmode=tk.MULTIPLE)
    subfolder_listbox.pack()

    for subfolder in subfolders:
        subfolder_listbox.insert(tk.END, subfolder)
        subfolder_listbox.selection_set(tk.END)

    def process_selected_subfolders():
        global selected_subfolders
        selected_subfolders = [subfolder_listbox.get(
            index) for index in subfolder_listbox.curselection()]
        file_extensions = get_file_extensions(folder_path, selected_subfolders)
        extension_listbox.delete(0, tk.END)
        for ext in file_extensions:
            extension_listbox.insert(tk.END, ext)
        subfolder_window.destroy()

    select_button = tk.Button(
        subfolder_window, text="Select Subfolders", command=process_selected_subfolders)
    select_button.pack()


def get_file_extensions(folder_path, selected_subfolders):
    file_extensions = set()

    # Get file extensions from the root folder
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            _, extension = os.path.splitext(file)
            file_extensions.add(extension)

    # Get file extensions from selected subfolders and their subfolders
    for subfolder in selected_subfolders:
        subfolder_path = os.path.join(folder_path, subfolder)
        for root, dirs, files in os.walk(subfolder_path):
            for file in files:
                _, extension = os.path.splitext(file)
                file_extensions.add(extension)

    return sorted(file_extensions)


def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        return file_path
    else:
        return None


def select_files():
    folder_path = folder_entry.get()
    selected_extensions = extension_listbox.curselection()
    file_extensions = [extension_listbox.get(
        index) for index in selected_extensions]

    if not folder_path or not file_extensions:
        messagebox.showwarning(
            "Warning", "Please provide folder path and select file extensions.")
        return

    files = []
    max_file_path_length = 0

    # Get files from the root folder
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(folder_path, file)
                files.append(file_path)
                max_file_path_length = max(
                    max_file_path_length, len(file_path))

    # Get files from selected subfolders and their subfolders
    for subfolder in selected_subfolders:
        subfolder_path = os.path.join(folder_path, subfolder)
        for root, dirs, filenames in os.walk(subfolder_path):
            for file in filenames:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    files.append(file_path)
                    max_file_path_length = max(
                        max_file_path_length, len(file_path))

    file_selection_window = tk.Toplevel(window)
    file_selection_window.title("Select Files")

    frame = tk.Frame(file_selection_window)
    frame.pack(fill=tk.BOTH, expand=True)

    file_listbox = tk.Listbox(
        frame, selectmode=tk.MULTIPLE, width=max_file_path_length)
    file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    file_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=file_listbox.yview)

    for file in files:
        file_listbox.insert(tk.END, file)
        file_listbox.selection_set(tk.END)

    def process_selected_files():
        selected_files = [file_listbox.get(index)
                          for index in file_listbox.curselection()]
        process_files(selected_files)
        file_selection_window.destroy()

    select_button = tk.Button(
        file_selection_window, text="Process Selected Files", command=process_selected_files)
    select_button.pack()


def process_files(selected_files):
    file_path = save_file()
    if not file_path:
        return

    with open(file_path, "w", encoding="utf-8") as output_file:
        for file in selected_files:
            relative_file_path = os.path.relpath(file, folder_entry.get())
            output_file.write(f"File: {relative_file_path}\n")
            output_file.write("-" * 50 + "\n")
            try:
                with open(file, "r", encoding="utf-8") as input_file:
                    output_file.write(input_file.read())
            except UnicodeDecodeError:
                try:
                    with open(file, "r", encoding="gbk") as input_file:
                        output_file.write(input_file.read())
                except UnicodeDecodeError:
                    try:
                        with open(file, "r", encoding="iso-8859-1") as input_file:
                            output_file.write(input_file.read())
                    except UnicodeDecodeError:
                        output_file.write("(Unable to decode file content)\n")
            output_file.write("\n\n")

    messagebox.showinfo("Success", "Files processed successfully.")


# Create the main window
window = tk.Tk()
window.title("File Processor")

# Create and pack the widgets
folder_label = tk.Label(window, text="Folder Path:")
folder_label.pack()

folder_entry = tk.Entry(window, width=50)
folder_entry.pack()

browse_button = tk.Button(window, text="Browse", command=browse_folder)
browse_button.pack()

extension_label = tk.Label(window, text="Select File Extensions:")
extension_label.pack()

extension_listbox = tk.Listbox(window, selectmode=tk.MULTIPLE)
extension_listbox.pack()

select_button = tk.Button(window, text="Select Files", command=select_files)
select_button.pack()

# Start the main event loop
window.mainloop()
