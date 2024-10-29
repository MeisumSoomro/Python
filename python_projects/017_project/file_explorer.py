import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
from datetime import datetime
import mimetypes
from PIL import Image, ImageTk

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("File Explorer")
        
        # Initialize path
        self.current_path = os.path.expanduser("~")
        
        # Create GUI elements
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
        # Load initial directory
        self.refresh_view()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Folder", command=self.create_folder)
        file_menu.add_command(label="Delete", command=self.delete_selected)
        file_menu.add_command(label="Rename", command=self.rename_selected)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy_selected)
        edit_menu.add_command(label="Cut", command=self.cut_selected)
        edit_menu.add_command(label="Paste", command=self.paste_items)
        
        # View menu
        self.view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Refresh", command=self.refresh_view)
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Navigation buttons
        ttk.Button(toolbar, text="←", command=self.go_back).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="↑", command=self.go_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⟳", command=self.refresh_view).pack(side=tk.LEFT, padx=2)
        
        # Path entry
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(toolbar, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.path_entry.bind('<Return>', lambda e: self.navigate_to_path())
        
    def create_main_layout(self):
        # Create paned window
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Create tree view for folders
        self.tree = ttk.Treeview(paned, columns=('Size', 'Modified'), selectmode='extended')
        self.tree.heading('#0', text='Name')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Modified')
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(paned, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Preview frame
        self.preview_frame = ttk.LabelFrame(paned, text="Preview")
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Add to paned window
        paned.add(self.tree, weight=3)
        paned.add(self.preview_frame, weight=1)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)
        
    def refresh_view(self):
        self.tree.delete(*self.tree.get_children())
        self.path_var.set(self.current_path)
        
        try:
            # List directories first
            for item in sorted(os.listdir(self.current_path)):
                full_path = os.path.join(self.current_path, item)
                size = self.get_size_str(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M')
                
                if os.path.isdir(full_path):
                    self.tree.insert('', 'end', text=item, values=(size, modified), tags=('directory',))
                else:
                    self.tree.insert('', 'end', text=item, values=(size, modified), tags=('file',))
                    
            self.update_status()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def get_size_str(self, path):
        try:
            if os.path.isdir(path):
                return '<DIR>'
            size = os.path.getsize(path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "N/A"
            
    def on_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            path = os.path.join(self.current_path, self.tree.item(item, 'text'))
            if os.path.isdir(path):
                self.current_path = path
                self.refresh_view()
            else:
                self.open_file(path)
                
    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            path = os.path.join(self.current_path, self.tree.item(item, 'text'))
            self.show_preview(path)
            
    def show_preview(self, path):
        if os.path.isfile(path):
            mime_type, _ = mimetypes.guess_type(path)
            if mime_type and mime_type.startswith('image/'):
                try:
                    image = Image.open(path)
                    image.thumbnail((200, 200))
                    photo = ImageTk.PhotoImage(image)
                    self.preview_label.configure(image=photo)
                    self.preview_label.image = photo
                except:
                    self.preview_label.configure(text="Cannot preview image")
            else:
                try:
                    with open(path, 'r') as f:
                        preview = f.read(500)
                    self.preview_label.configure(text=preview)
                except:
                    self.preview_label.configure(text="Cannot preview file")
        else:
            self.preview_label.configure(text="")
            
    def go_back(self):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            self.refresh_view()
            
    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if os.path.exists(parent):
            self.current_path = parent
            self.refresh_view()
            
    def navigate_to_path(self):
        path = self.path_var.get()
        if os.path.exists(path):
            self.current_path = path
            self.refresh_view()
        else:
            messagebox.showerror("Error", "Invalid path")
            
    def create_folder(self):
        name = tk.simpledialog.askstring("New Folder", "Enter folder name:")
        if name:
            path = os.path.join(self.current_path, name)
            try:
                os.makedirs(path)
                self.refresh_view()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete selected items?"):
            for item in selection:
                path = os.path.join(self.current_path, self.tree.item(item, 'text'))
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete {path}: {str(e)}")
            self.refresh_view()
            
    def rename_selected(self):
        selection = self.tree.selection()
        if len(selection) != 1:
            return
            
        old_name = self.tree.item(selection[0], 'text')
        new_name = tk.simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            old_path = os.path.join(self.current_path, old_name)
            new_path = os.path.join(self.current_path, new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh_view()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def update_status(self):
        total_items = len(self.tree.get_children())
        self.status_bar.config(text=f"Total items: {total_items}")
        
    def open_file(self, path):
        try:
            os.startfile(path)
        except:
            messagebox.showerror("Error", "Could not open file")
            
    # Clipboard operations
    def copy_selected(self):
        self.clipboard = []
        self.clipboard_op = 'copy'
        for item in self.tree.selection():
            path = os.path.join(self.current_path, self.tree.item(item, 'text'))
            self.clipboard.append(path)
            
    def cut_selected(self):
        self.clipboard = []
        self.clipboard_op = 'cut'
        for item in self.tree.selection():
            path = os.path.join(self.current_path, self.tree.item(item, 'text'))
            self.clipboard.append(path)
            
    def paste_items(self):
        if not hasattr(self, 'clipboard') or not self.clipboard:
            return
            
        for src in self.clipboard:
            name = os.path.basename(src)
            dst = os.path.join(self.current_path, name)
            
            try:
                if os.path.isdir(src):
                    if self.clipboard_op == 'copy':
                        shutil.copytree(src, dst)
                    else:
                        shutil.move(src, dst)
                else:
                    if self.clipboard_op == 'copy':
                        shutil.copy2(src, dst)
                    else:
                        shutil.move(src, dst)
            except Exception as e:
                messagebox.showerror("Error", f"Could not paste {name}: {str(e)}")
                
        if self.clipboard_op == 'cut':
            self.clipboard = []
        self.refresh_view()

def main():
    root = tk.Tk()
    root.geometry("1000x600")
    app = FileExplorer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 