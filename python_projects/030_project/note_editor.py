import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from tkhtmlview import HTMLLabel, HTMLScrolledText
import markdown
from note_database import NoteDatabase
from note_sync import CloudSync

class NoteEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Note Editor")
        
        # Initialize handlers
        self.db = NoteDatabase()
        self.sync = CloudSync()
        
        # Note categories
        self.categories = ["Personal", "Work", "Study", "Ideas", 
                         "Projects", "Tasks", "Other"]
        
        # Current note
        self.current_note = None
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Load notes
        self.load_notes()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Note", command=self.new_note)
        file_menu.add_command(label="Import Notes", command=self.import_notes)
        file_menu.add_command(label="Export Notes", command=self.export_notes)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Bold", command=lambda: self.format_text('**'))
        edit_menu.add_command(label="Italic", command=lambda: self.format_text('*'))
        edit_menu.add_command(label="Code", command=lambda: self.format_text('`'))
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Preview", command=self.toggle_preview)
        
        # Sync menu
        sync_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sync", menu=sync_menu)
        sync_menu.add_command(label="Sync Now", command=self.sync_notes)
        sync_menu.add_command(label="Sync Settings", command=self.sync_settings)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel with notes list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Search
        search_frame = ttk.LabelFrame(left_frame, text="Search")
        search_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_notes)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X, 
                                                                  padx=5, pady=5)
        
        # Category filter
        filter_frame = ttk.LabelFrame(left_frame, text="Filter")
        filter_frame.pack(fill=tk.X, pady=5)
        
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, 
                                    values=["All"] + self.categories,
                                    textvariable=self.category_var)
        category_combo.pack(fill=tk.X, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_notes)
        
        # Notes list
        list_frame = ttk.LabelFrame(left_frame, text="Notes")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.notes_list = tk.Listbox(list_frame)
        self.notes_list.pack(fill=tk.BOTH, expand=True)
        self.notes_list.bind('<<ListboxSelect>>', self.load_note)
        
        # Quick add note
        ttk.Button(left_frame, text="New Note", 
                  command=self.new_note).pack(fill=tk.X, pady=5)
        
        # Right panel with editor
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Note details
        details_frame = ttk.Frame(right_frame)
        details_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(details_frame, text="Title:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(details_frame)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(details_frame, text="Category:").pack(side=tk.LEFT)
        self.note_category = ttk.Combobox(details_frame, values=self.categories)
        self.note_category.pack(side=tk.LEFT, padx=5)
        
        # Editor and preview
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Editor tab
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="Editor")
        
        self.editor = HTMLScrolledText(editor_frame)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Preview tab
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="Preview")
        
        self.preview = HTMLLabel(preview_frame)
        self.preview.pack(fill=tk.BOTH, expand=True)
        
        # Save button
        ttk.Button(right_frame, text="Save", 
                  command=self.save_note).pack(fill=tk.X, pady=5)
        
    def new_note(self):
        """Create new note"""
        self.current_note = None
        self.title_entry.delete(0, tk.END)
        self.note_category.set('')
        self.editor.delete('1.0', tk.END)
        self.notebook.select(0)  # Switch to editor tab
        
    def save_note(self):
        """Save current note"""
        title = self.title_entry.get().strip()
        category = self.note_category.get().strip()
        content = self.editor.get('1.0', tk.END).strip()
        
        if not all([title, category, content]):
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
            
        note = {
            'title': title,
            'category': category,
            'content': content,
            'modified_date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        if self.current_note:
            note['id'] = self.current_note['id']
            self.db.update_note(note)
        else:
            self.db.add_note(note)
            
        self.load_notes()
        messagebox.showinfo("Success", "Note saved!")
        
    def load_note(self, event=None):
        """Load selected note into editor"""
        selection = self.notes_list.curselection()
        if not selection:
            return
            
        note_id = self.notes_list.get(selection[0]).split()[0]
        self.current_note = self.db.get_note(note_id)
        
        if self.current_note:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self.current_note['title'])
            
            self.note_category.set(self.current_note['category'])
            
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', self.current_note['content'])
            
            self.update_preview()
            
    def format_text(self, marker):
        """Add markdown formatting to selected text"""
        try:
            selection = self.editor.tag_ranges(tk.SEL)
            if selection:
                start, end = selection
                text = self.editor.get(start, end)
                self.editor.delete(start, end)
                self.editor.insert(start, f"{marker}{text}{marker}")
        except tk.TclError:
            pass
            
    def toggle_preview(self):
        """Toggle between editor and preview"""
        if self.notebook.select() == 0:  # Currently on editor
            self.update_preview()
            self.notebook.select(1)  # Switch to preview
        else:
            self.notebook.select(0)  # Switch to editor
            
    def update_preview(self):
        """Update preview with rendered markdown"""
        content = self.editor.get('1.0', tk.END)
        html = markdown.markdown(content)
        self.preview.set_html(html)
        
    def search_notes(self, *args):
        """Search notes by title and content"""
        search_text = self.search_var.get().lower()
        category = self.category_var.get()
        
        notes = self.db.search_notes(search_text, category)
        self.update_notes_list(notes)
        
    def filter_notes(self, event=None):
        """Filter notes by category"""
        self.search_notes()
        
    def update_notes_list(self, notes):
        """Update notes list with search/filter results"""
        self.notes_list.delete(0, tk.END)
        for note in notes:
            self.notes_list.insert(tk.END, 
                                 f"{note['id']} - {note['title']}")
            
    def load_notes(self):
        """Load all notes from database"""
        notes = self.db.get_all_notes()
        self.update_notes_list(notes)
        
    def sync_notes(self):
        """Sync notes with cloud storage"""
        try:
            self.sync.sync_notes()
            messagebox.showinfo("Success", "Notes synced successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Sync failed: {str(e)}")
            
    def sync_settings(self):
        """Show sync settings dialog"""
        self.sync.show_settings(self.root)
        
    def import_notes(self):
        """Import notes from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.db.import_notes(file_path)
                self.load_notes()
                messagebox.showinfo("Success", "Notes imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not import notes: {str(e)}")
                
    def export_notes(self):
        """Export notes to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.db.export_notes(file_path)
                messagebox.showinfo("Success", "Notes exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export notes: {str(e)}")

def main():
    root = tk.Tk()
    root.geometry("1200x800")
    app = NoteEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main() 