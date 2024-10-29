import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from ttkwidgets import CheckboxTreeview
import markdown2
from tkinter import font
from tkinter.scrolledtext import ScrolledText

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note Taking App")
        
        # Initialize variables
        self.current_note = None
        self.notes_data = {}
        self.categories = set()
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Load existing notes
        self.load_notes()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Note", command=self.new_note)
        file_menu.add_command(label="Save", command=self.save_note)
        file_menu.add_command(label="Export as Markdown", command=self.export_markdown)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.text_editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_editor.event_generate("<<Paste>>"))
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=lambda: self.format_text('bold'))
        format_menu.add_command(label="Italic", command=lambda: self.format_text('italic'))
        format_menu.add_command(label="Underline", command=lambda: self.format_text('underline'))
        
    def create_main_layout(self):
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for notes list and categories
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Category and search frame
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search box
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_notes)
        ttk.Entry(control_frame, textvariable=self.search_var).pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Notes tree
        self.notes_tree = CheckboxTreeview(left_frame)
        self.notes_tree.pack(fill=tk.BOTH, expand=True, padx=5)
        self.notes_tree.heading('#0', text='Notes')
        self.notes_tree.bind('<<TreeviewSelect>>', self.load_selected_note)
        
        # Right panel for note editing
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)
        
        # Note title
        title_frame = ttk.Frame(right_frame)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Title:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame)
        self.title_entry.pack(fill=tk.X, expand=True, padx=5)
        
        # Category selection
        cat_frame = ttk.Frame(right_frame)
        cat_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(cat_frame, text="Category:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var)
        self.category_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(cat_frame, text="New Category", command=self.new_category).pack(side=tk.LEFT)
        
        # Toolbar
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Text formatting buttons
        ttk.Button(toolbar, text="B", width=3, command=lambda: self.format_text('bold')).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="I", width=3, command=lambda: self.format_text('italic')).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="U", width=3, command=lambda: self.format_text('underline')).pack(side=tk.LEFT, padx=2)
        
        # Text editor
        self.text_editor = ScrolledText(right_frame, wrap=tk.WORD, undo=True)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def new_note(self):
        self.save_current_note()
        self.current_note = str(datetime.now().timestamp())
        self.title_entry.delete(0, tk.END)
        self.text_editor.delete(1.0, tk.END)
        self.category_var.set('')
        self.update_notes_tree()
        
    def save_note(self):
        if not self.current_note:
            return
            
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a title for the note")
            return
            
        content = self.text_editor.get(1.0, tk.END).strip()
        category = self.category_var.get()
        
        self.notes_data[self.current_note] = {
            'title': title,
            'content': content,
            'category': category,
            'modified': datetime.now().isoformat()
        }
        
        self.save_notes_to_file()
        self.update_notes_tree()
        
    def save_current_note(self):
        if self.current_note:
            self.save_note()
            
    def load_selected_note(self, event=None):
        selection = self.notes_tree.selection()
        if selection:
            note_id = selection[0]
            if note_id in self.notes_data:
                self.current_note = note_id
                note = self.notes_data[note_id]
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, note['title'])
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, note['content'])
                self.category_var.set(note.get('category', ''))
                
    def update_notes_tree(self):
        self.notes_tree.delete(*self.notes_tree.get_children())
        
        # Group notes by category
        categorized_notes = {}
        for note_id, note in self.notes_data.items():
            category = note.get('category', 'Uncategorized')
            if category not in categorized_notes:
                categorized_notes[category] = []
            categorized_notes[category].append((note_id, note))
            
        # Add to tree
        for category in sorted(categorized_notes.keys()):
            category_id = self.notes_tree.insert('', 'end', text=category)
            for note_id, note in sorted(categorized_notes[category], key=lambda x: x[1]['title']):
                self.notes_tree.insert(category_id, 'end', note_id, text=note['title'])
                
    def filter_notes(self, *args):
        search_term = self.search_var.get().lower()
        self.update_notes_tree()
        if search_term:
            for item in self.notes_tree.get_children():
                # Check category items
                for note_item in self.notes_tree.get_children(item):
                    if search_term not in self.notes_tree.item(note_item)['text'].lower():
                        self.notes_tree.detach(note_item)
                # Remove empty categories
                if not self.notes_tree.get_children(item):
                    self.notes_tree.detach(item)
                    
    def new_category(self):
        category = tk.simpledialog.askstring("New Category", "Enter category name:")
        if category:
            self.categories.add(category)
            self.update_category_list()
            self.category_var.set(category)
            
    def update_category_list(self):
        categories = sorted(list(self.categories))
        self.category_combo['values'] = categories
        
    def format_text(self, style):
        try:
            selection = self.text_editor.tag_ranges(tk.SEL)
            if selection:
                current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
                if style in current_tags:
                    self.text_editor.tag_remove(style, tk.SEL_FIRST, tk.SEL_LAST)
                else:
                    self.text_editor.tag_add(style, tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
            
    def export_markdown(self):
        if not self.current_note:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            content = self.text_editor.get(1.0, tk.END).strip()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {self.title_entry.get()}\n\n")
                f.write(content)
                
    def save_notes_to_file(self):
        try:
            with open('notes.json', 'w') as f:
                json.dump(self.notes_data, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save notes: {str(e)}")
            
    def load_notes(self):
        try:
            if os.path.exists('notes.json'):
                with open('notes.json', 'r') as f:
                    self.notes_data = json.load(f)
                    
                # Extract categories
                self.categories = set(note.get('category', '') 
                                   for note in self.notes_data.values())
                self.categories.discard('')
                self.update_category_list()
                self.update_notes_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load notes: {str(e)}")
            
    def on_closing(self):
        self.save_current_note()
        self.root.destroy()

def main():
    root = tk.Tk()
    root.geometry("1000x600")
    app = NoteApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 