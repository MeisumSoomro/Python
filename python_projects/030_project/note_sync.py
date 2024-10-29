import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from dropbox import Dropbox
from dropbox.exceptions import AuthError
from datetime import datetime

class CloudSync:
    def __init__(self):
        self.config_file = 'sync_config.json'
        self.config = self.load_config()
        self.dbx = None
        
        if self.config.get('access_token'):
            self.initialize_dropbox()
            
    def load_config(self):
        """Load sync configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_config(self):
        """Save sync configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
            
    def initialize_dropbox(self):
        """Initialize Dropbox client"""
        try:
            self.dbx = Dropbox(self.config['access_token'])
            self.dbx.users_get_current_account()
        except AuthError:
            self.dbx = None
            self.config['access_token'] = None
            self.save_config()
            
    def show_settings(self, parent):
        """Show sync settings dialog"""
        settings = tk.Toplevel(parent)
        settings.title("Sync Settings")
        settings.geometry("400x300")
        
        # Dropbox settings
        dropbox_frame = ttk.LabelFrame(settings, text="Dropbox")
        dropbox_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dropbox_frame, text="Access Token:").pack(pady=2)
        token_entry = ttk.Entry(dropbox_frame)
        if self.config.get('access_token'):
            token_entry.insert(0, self.config['access_token'])
        token_entry.pack(fill=tk.X, padx=5)
        
        def save_settings():
            token = token_entry.get().strip()
            if token:
                self.config['access_token'] = token
                self.save_config()
                self.initialize_dropbox()
                if self.dbx:
                    messagebox.showinfo("Success", "Dropbox connected successfully!")
                    settings.destroy()
                else:
                    messagebox.showerror("Error", "Invalid access token")
                    
        ttk.Button(settings, text="Save", 
                  command=save_settings).pack(pady=10)
        
    def sync_notes(self):
        """Sync notes with cloud storage"""
        if not self.dbx:
            raise Exception("Cloud storage not configured")
            
        # Upload local database
        with open('notes.db', 'rb') as f:
            self.dbx.files_upload(
                f.read(),
                '/notes.db',
                mode=dropbox.files.WriteMode.overwrite
            )
            
        # Download cloud changes
        try:
            metadata, response = self.dbx.files_download('/notes.db')
            with open('notes.db', 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading changes: {str(e)}") 