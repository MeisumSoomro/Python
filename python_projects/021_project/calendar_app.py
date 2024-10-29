import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime, timedelta
import json
import os
from tkcalendar import Calendar
from collections import defaultdict

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar App")
        
        # Initialize variables
        self.current_date = datetime.now()
        self.events = defaultdict(list)
        self.selected_date = None
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Load existing events
        self.load_events()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Event", command=self.new_event)
        file_menu.add_command(label="Export Events", command=self.export_events)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Day View", command=lambda: self.change_view("day"))
        view_menu.add_command(label="Week View", command=lambda: self.change_view("week"))
        view_menu.add_command(label="Month View", command=lambda: self.change_view("month"))
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel with calendar
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Calendar widget
        self.cal = Calendar(left_frame, selectmode='day',
                          year=self.current_date.year,
                          month=self.current_date.month,
                          day=self.current_date.day)
        self.cal.pack(fill=tk.BOTH, expand=True)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)
        
        # Quick add event
        ttk.Button(left_frame, text="Add Event", command=self.new_event).pack(fill=tk.X, pady=5)
        
        # Right panel with events
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Events list
        events_frame = ttk.LabelFrame(right_frame, text="Events")
        events_frame.pack(fill=tk.BOTH, expand=True)
        
        # Events treeview
        columns = ('Time', 'Title', 'Description')
        self.events_tree = ttk.Treeview(events_frame, columns=columns, show='headings')
        for col in columns:
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=100)
        
        self.events_tree.pack(fill=tk.BOTH, expand=True)
        self.events_tree.bind('<Double-1>', self.edit_event)
        
        # Scrollbar for events
        scrollbar = ttk.Scrollbar(events_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
    def new_event(self):
        event_window = tk.Toplevel(self.root)
        event_window.title("New Event")
        event_window.geometry("400x300")
        
        # Event details
        ttk.Label(event_window, text="Title:").pack(padx=5, pady=2)
        title_entry = ttk.Entry(event_window)
        title_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(event_window, text="Date:").pack(padx=5, pady=2)
        date_entry = ttk.Entry(event_window)
        date_entry.insert(0, self.cal.get_date())
        date_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(event_window, text="Time:").pack(padx=5, pady=2)
        time_entry = ttk.Entry(event_window)
        time_entry.insert(0, "00:00")
        time_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(event_window, text="Description:").pack(padx=5, pady=2)
        desc_text = tk.Text(event_window, height=4)
        desc_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        def save_event():
            title = title_entry.get().strip()
            date = date_entry.get().strip()
            time = time_entry.get().strip()
            desc = desc_text.get(1.0, tk.END).strip()
            
            if not all([title, date, time]):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            event = {
                'title': title,
                'time': time,
                'description': desc
            }
            
            self.events[date].append(event)
            self.save_events()
            self.update_events_list()
            event_window.destroy()
            
        ttk.Button(event_window, text="Save", command=save_event).pack(pady=10)
        
    def edit_event(self, event=None):
        selection = self.events_tree.selection()
        if not selection:
            return
            
        item = self.events_tree.item(selection[0])
        date = self.cal.get_date()
        time = item['values'][0]
        title = item['values'][1]
        desc = item['values'][2]
        
        # Find event in list
        event_list = self.events[date]
        event_index = next((i for i, e in enumerate(event_list) 
                          if e['title'] == title and e['time'] == time), None)
        
        if event_index is None:
            return
            
        event_window = tk.Toplevel(self.root)
        event_window.title("Edit Event")
        event_window.geometry("400x300")
        
        ttk.Label(event_window, text="Title:").pack(padx=5, pady=2)
        title_entry = ttk.Entry(event_window)
        title_entry.insert(0, title)
        title_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(event_window, text="Time:").pack(padx=5, pady=2)
        time_entry = ttk.Entry(event_window)
        time_entry.insert(0, time)
        time_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(event_window, text="Description:").pack(padx=5, pady=2)
        desc_text = tk.Text(event_window, height=4)
        desc_text.insert(1.0, desc)
        desc_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        def update_event():
            new_title = title_entry.get().strip()
            new_time = time_entry.get().strip()
            new_desc = desc_text.get(1.0, tk.END).strip()
            
            if not all([new_title, new_time]):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            event_list[event_index] = {
                'title': new_title,
                'time': new_time,
                'description': new_desc
            }
            
            self.save_events()
            self.update_events_list()
            event_window.destroy()
            
        def delete_event():
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this event?"):
                event_list.pop(event_index)
                self.save_events()
                self.update_events_list()
                event_window.destroy()
                
        button_frame = ttk.Frame(event_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Update", command=update_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_event).pack(side=tk.LEFT, padx=5)
        
    def on_date_select(self, event=None):
        self.selected_date = self.cal.get_date()
        self.update_events_list()
        
    def update_events_list(self):
        self.events_tree.delete(*self.events_tree.get_children())
        if not self.selected_date:
            return
            
        for event in sorted(self.events[self.selected_date], key=lambda x: x['time']):
            self.events_tree.insert('', 'end', values=(
                event['time'],
                event['title'],
                event['description']
            ))
            
    def change_view(self, view_type):
        # Implement different calendar views
        pass
        
    def export_events(self):
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(dict(self.events), f)
                messagebox.showinfo("Success", "Events exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export events: {str(e)}")
                
    def save_events(self):
        try:
            with open('calendar_events.json', 'w') as f:
                json.dump(dict(self.events), f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save events: {str(e)}")
            
    def load_events(self):
        try:
            if os.path.exists('calendar_events.json'):
                with open('calendar_events.json', 'r') as f:
                    self.events = defaultdict(list, json.load(f))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load events: {str(e)}")
            
    def on_closing(self):
        self.save_events()
        self.root.destroy()

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = CalendarApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 