import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
from mutagen.mp3 import MP3
from PIL import Image, ImageTk
import json
import time
from threading import Thread

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Player state
        self.current_track = None
        self.playing = False
        self.paused = False
        self.current_playlist = []
        self.current_index = -1
        
        # Create GUI elements
        self.create_menu()
        self.create_player_frame()
        self.create_playlist_frame()
        self.create_controls()
        
        # Start update thread
        self.update_thread = Thread(target=self.update_player, daemon=True)
        self.update_thread.start()
        
        # Load last session
        self.load_session()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files", command=self.add_files)
        file_menu.add_command(label="Add Folder", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Save Playlist", command=self.save_playlist)
        file_menu.add_command(label="Load Playlist", command=self.load_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
    def create_player_frame(self):
        player_frame = ttk.LabelFrame(self.root, text="Now Playing")
        player_frame.pack(padx=5, pady=5, fill=tk.X)
        
        # Track info
        self.track_var = tk.StringVar(value="No track selected")
        track_label = ttk.Label(player_frame, textvariable=self.track_var)
        track_label.pack(pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(player_frame, from_=0, to=100,
                                    orient=tk.HORIZONTAL, variable=self.progress_var,
                                    command=self.seek)
        self.progress_bar.pack(fill=tk.X, padx=5)
        
        # Time labels
        time_frame = ttk.Frame(player_frame)
        time_frame.pack(fill=tk.X, padx=5)
        self.current_time_var = tk.StringVar(value="00:00")
        self.total_time_var = tk.StringVar(value="00:00")
        ttk.Label(time_frame, textvariable=self.current_time_var).pack(side=tk.LEFT)
        ttk.Label(time_frame, textvariable=self.total_time_var).pack(side=tk.RIGHT)
        
    def create_playlist_frame(self):
        playlist_frame = ttk.LabelFrame(self.root, text="Playlist")
        playlist_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Playlist view
        self.playlist = ttk.Treeview(playlist_frame, columns=('Duration',),
                                   selectmode='browse')
        self.playlist.heading('#0', text='Track')
        self.playlist.heading('Duration', text='Duration')
        self.playlist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(playlist_frame, orient=tk.VERTICAL,
                                command=self.playlist.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click
        self.playlist.bind('<Double-1>', self.play_selected)
        
    def create_controls(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(padx=5, pady=5)
        
        # Control buttons
        ttk.Button(control_frame, text="⏮", command=self.previous_track).pack(side=tk.LEFT, padx=2)
        self.play_button = ttk.Button(control_frame, text="▶", command=self.play_pause)
        self.play_button.pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="⏭", command=self.next_track).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="⏹", command=self.stop).pack(side=tk.LEFT, padx=2)
        
        # Volume control
        ttk.Label(control_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
        self.volume_var = tk.DoubleVar(value=70)
        volume_scale = ttk.Scale(control_frame, from_=0, to=100,
                               orient=tk.HORIZONTAL, variable=self.volume_var,
                               command=self.set_volume)
        volume_scale.pack(side=tk.LEFT, padx=5)
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        for file in files:
            self.add_to_playlist(file)
            
    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.mp3'):
                        self.add_to_playlist(os.path.join(root, file))
                        
    def add_to_playlist(self, file_path):
        try:
            audio = MP3(file_path)
            duration = time.strftime('%M:%S', time.gmtime(audio.info.length))
            name = os.path.basename(file_path)
            self.playlist.insert('', 'end', text=name, values=(duration,))
            self.current_playlist.append(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not add {file_path}: {str(e)}")
            
    def play_selected(self, event=None):
        selection = self.playlist.selection()
        if selection:
            index = self.playlist.index(selection[0])
            self.play_track(index)
            
    def play_track(self, index):
        if 0 <= index < len(self.current_playlist):
            try:
                pygame.mixer.music.load(self.current_playlist[index])
                pygame.mixer.music.play()
                self.playing = True
                self.paused = False
                self.current_index = index
                self.current_track = self.current_playlist[index]
                self.update_track_info()
                self.play_button.configure(text="⏸")
            except Exception as e:
                messagebox.showerror("Error", f"Could not play track: {str(e)}")
                
    def play_pause(self):
        if not self.current_track:
            self.play_selected()
        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_button.configure(text="⏸")
        elif self.playing:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_button.configure(text="▶")
        else:
            self.play_track(self.current_index)
            
    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_button.configure(text="▶")
        
    def next_track(self):
        if self.current_index < len(self.current_playlist) - 1:
            self.play_track(self.current_index + 1)
            
    def previous_track(self):
        if self.current_index > 0:
            self.play_track(self.current_index - 1)
            
    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value) / 100)
        
    def seek(self, value):
        if self.current_track:
            position = float(value)
            audio = MP3(self.current_track)
            time_to_seek = (position / 100) * audio.info.length
            pygame.mixer.music.play(start=time_to_seek)
            
    def update_track_info(self):
        if self.current_track:
            name = os.path.basename(self.current_track)
            self.track_var.set(name)
            audio = MP3(self.current_track)
            duration = time.strftime('%M:%S', time.gmtime(audio.info.length))
            self.total_time_var.set(duration)
            
    def update_player(self):
        while True:
            if self.playing and not self.paused and self.current_track:
                try:
                    audio = MP3(self.current_track)
                    current_pos = pygame.mixer.music.get_pos() / 1000
                    progress = (current_pos / audio.info.length) * 100
                    self.progress_var.set(progress)
                    
                    current_time = time.strftime('%M:%S', time.gmtime(current_pos))
                    self.current_time_var.set(current_time)
                    
                    if not pygame.mixer.music.get_busy() and not self.paused:
                        self.next_track()
                except:
                    pass
            time.sleep(0.1)
            
    def save_playlist(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.current_playlist, f)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save playlist: {str(e)}")
                
    def load_playlist(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    playlist = json.load(f)
                self.playlist.delete(*self.playlist.get_children())
                self.current_playlist = []
                for track in playlist:
                    self.add_to_playlist(track)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load playlist: {str(e)}")
                
    def save_session(self):
        try:
            session = {
                'playlist': self.current_playlist,
                'current_index': self.current_index,
                'volume': self.volume_var.get()
            }
            with open('session.json', 'w') as f:
                json.dump(session, f)
        except:
            pass
            
    def load_session(self):
        try:
            with open('session.json', 'r') as f:
                session = json.load(f)
            for track in session['playlist']:
                self.add_to_playlist(track)
            self.volume_var.set(session['volume'])
            self.set_volume(session['volume'])
        except:
            pass
            
    def on_closing(self):
        self.save_session()
        self.root.destroy()

def main():
    root = tk.Tk()
    root.geometry("600x400")
    app = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 