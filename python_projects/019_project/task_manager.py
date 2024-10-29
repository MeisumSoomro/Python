import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import time
from datetime import datetime
import threading
import platform
import os

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        
        # Initialize variables
        self.selected_pid = None
        self.update_interval = 1000  # milliseconds
        self.sort_by = "cpu"
        self.sort_reverse = True
        
        # Create GUI elements
        self.create_menu()
        self.create_system_info()
        self.create_process_view()
        self.create_details_view()
        
        # Start updates
        self.update_data()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Run New Task", command=self.run_new_task)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Now", command=self.update_data)
        
    def create_system_info(self):
        info_frame = ttk.LabelFrame(self.root, text="System Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # CPU Usage
        cpu_frame = ttk.Frame(info_frame)
        cpu_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(cpu_frame, text="CPU Usage:").pack(side=tk.LEFT)
        self.cpu_progress = ttk.Progressbar(cpu_frame, length=200, mode='determinate')
        self.cpu_progress.pack(side=tk.LEFT, padx=5)
        self.cpu_label = ttk.Label(cpu_frame, text="0%")
        self.cpu_label.pack(side=tk.LEFT)
        
        # Memory Usage
        mem_frame = ttk.Frame(info_frame)
        mem_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(mem_frame, text="Memory Usage:").pack(side=tk.LEFT)
        self.mem_progress = ttk.Progressbar(mem_frame, length=200, mode='determinate')
        self.mem_progress.pack(side=tk.LEFT, padx=5)
        self.mem_label = ttk.Label(mem_frame, text="0/0 GB")
        self.mem_label.pack(side=tk.LEFT)
        
        # Disk Usage
        disk_frame = ttk.Frame(info_frame)
        disk_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(disk_frame, text="Disk Usage:").pack(side=tk.LEFT)
        self.disk_progress = ttk.Progressbar(disk_frame, length=200, mode='determinate')
        self.disk_progress.pack(side=tk.LEFT, padx=5)
        self.disk_label = ttk.Label(disk_frame, text="0/0 GB")
        self.disk_label.pack(side=tk.LEFT)
        
    def create_process_view(self):
        # Process list
        process_frame = ttk.LabelFrame(self.root, text="Processes")
        process_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('PID', 'Name', 'CPU', 'Memory', 'Status', 'User')
        self.tree = ttk.Treeview(process_frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_processes(c))
            self.tree.column(col, width=100)
            
        # Add scrollbars
        vsb = ttk.Scrollbar(process_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(process_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        process_frame.grid_columnconfigure(0, weight=1)
        process_frame.grid_rowconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_select_process)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
    def create_details_view(self):
        details_frame = ttk.LabelFrame(self.root, text="Process Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.details_text = tk.Text(details_frame, height=4, wrap=tk.WORD)
        self.details_text.pack(fill=tk.X, padx=5, pady=5)
        
    def update_data(self):
        self.update_system_info()
        self.update_process_list()
        self.root.after(self.update_interval, self.update_data)
        
    def update_system_info(self):
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_progress['value'] = cpu_percent
        self.cpu_label['text'] = f"{cpu_percent:.1f}%"
        
        # Memory
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        self.mem_progress['value'] = mem_percent
        self.mem_label['text'] = f"{mem.used/1024/1024/1024:.1f}/{mem.total/1024/1024/1024:.1f} GB"
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        self.disk_progress['value'] = disk_percent
        self.disk_label['text'] = f"{disk.used/1024/1024/1024:.1f}/{disk.total/1024/1024/1024:.1f} GB"
        
    def update_process_list(self):
        # Clear current items
        self.tree.delete(*self.tree.get_children())
        
        # Get process list
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
            try:
                pinfo = proc.info
                processes.append([
                    str(pinfo['pid']),
                    pinfo['name'],
                    f"{pinfo['cpu_percent']:.1f}",
                    f"{pinfo['memory_percent']:.1f}",
                    pinfo['status'],
                    pinfo['username']
                ])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        # Sort processes
        processes.sort(key=lambda x: float(x[2]), reverse=self.sort_reverse)
        
        # Insert into treeview
        for proc in processes:
            self.tree.insert('', 'end', values=proc)
            
    def sort_processes(self, column):
        self.sort_by = column
        self.sort_reverse = not self.sort_reverse
        self.update_process_list()
        
    def on_select_process(self, event):
        selection = self.tree.selection()
        if selection:
            pid = self.tree.item(selection[0])['values'][0]
            self.selected_pid = int(pid)
            self.update_process_details()
            
    def update_process_details(self):
        try:
            process = psutil.Process(self.selected_pid)
            details = f"Name: {process.name()}\n"
            details += f"PID: {process.pid}\n"
            details += f"Status: {process.status()}\n"
            details += f"Created: {datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, details)
        except psutil.NoSuchProcess:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, "Process not found")
            
    def show_context_menu(self, event):
        selection = self.tree.selection()
        if selection:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="End Process", command=self.end_process)
            menu.post(event.x_root, event.y_root)
            
    def end_process(self):
        if self.selected_pid:
            if messagebox.askyesno("Confirm", "Are you sure you want to end this process?"):
                try:
                    process = psutil.Process(self.selected_pid)
                    process.terminate()
                    self.update_process_list()
                except psutil.NoSuchProcess:
                    messagebox.showerror("Error", "Process not found")
                except psutil.AccessDenied:
                    messagebox.showerror("Error", "Access denied")
                    
    def run_new_task(self):
        command = tk.simpledialog.askstring("Run New Task", "Enter command:")
        if command:
            try:
                if platform.system() == 'Windows':
                    os.system(f'start {command}')
                else:
                    os.system(f'{command} &')
            except Exception as e:
                messagebox.showerror("Error", f"Could not run command: {str(e)}")

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = TaskManager(root)
    root.mainloop()

if __name__ == "__main__":
    main() 