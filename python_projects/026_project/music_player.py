import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
import os
from mutagen.mp3 import MP3
from datetime import timedelta
import json
from playlist_manager import PlaylistManager
from audio_visualizer import AudioVisualizer

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Initialize managers
        self.playlist = PlaylistManager()
        self.visualizer = AudioVisualizer(self.root)
        
        # Player state
        self.current_track = None
        self.playing = False
        self.current_time = 0
        self.track_length = 0
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Start update loop
        self.update_player()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files", command=self.add_files)
        file_menu.add_command(label="Add Folder", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Playlist menu
        playlist_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Playlist", menu=playlist_menu)
        playlist_menu.add_command(label="Save Playlist", command=self.save_playlist)
        playlist_menu.add_command(label="Load Playlist", command=self.load_playlist)
        playlist_menu.add_command(label="Clear Playlist", command=self.clear_playlist)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Visualizer", 
                            command=self.visualizer.show_window)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Now playing frame
        now_playing_frame = ttk.LabelFrame(main_frame, text="Now Playing")
        now_playing_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.track_label = ttk.Label(now_playing_frame, 
                                   text="No track selected", 
                                   font=('Arial', 10))
        self.track_label.pack(pady=5)
        
        # Progress frame
        progress_frame = ttk.Frame(now_playing_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.time_label = ttk.Label(progress_frame, text="0:00 / 0:00")
        self.time_label.pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(progress_frame, 
                                    from_=0, to=100,
                                    orient=tk.HORIZONTAL,
                                    variable=self.progress_var,
                                    command=self.seek)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Controls frame
        controls_frame = ttk.Frame(now_playing_frame)
        controls_frame.pack(pady=5)
        
        # Previous button
        ttk.Button(controls_frame, text="⏮", width=3,
                  command=self.previous_track).pack(side=tk.LEFT, padx=2)
        
        # Play/Pause button
        self.play_button = ttk.Button(controls_frame, text="▶", width=3,
                                    command=self.play_pause)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        # Next button
        ttk.Button(controls_frame, text="⏭", width=3,
                  command=self.next_track).pack(side=tk.LEFT, padx=2)
        
        # Volume control
        volume_frame = ttk.Frame(controls_frame)
        volume_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(volume_frame, text="🔊").pack(side=tk.LEFT)
        self.volume_var = tk.DoubleVar(value=70)
        volume_scale = ttk.Scale(volume_frame, from_=0, to=100,
                               orient=tk.HORIZONTAL, length=100,
                               variable=self.volume_var,
                               command=self.set_volume)
        volume_scale.pack(side=tk.LEFT)
        
        # Playlist frame
        playlist_frame = ttk.LabelFrame(main_frame, text="Playlist")
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Playlist treeview
        columns = ('Title', 'Artist', 'Duration')
        self.playlist_tree = ttk.Treeview(playlist_frame, columns=columns, 
                                        show='headings')
        
        for col in columns:
            self.playlist_tree.heading(col, text=col)
            self.playlist_tree.column(col, width=100)
        
        self.playlist_tree.pack(fill=tk.BOTH, expand=True)
        self.playlist_tree.bind('<Double-1>', self.play_selected)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(playlist_frame, orient=tk.VERTICAL, 
                                command=self.playlist_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_tree.configure(yscrollcommand=scrollbar.set)
        
        # Set initial volume
        self.set_volume(70)
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if files:
            self.playlist.add_files(files)
            self.update_playlist_view()
            
    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.playlist.add_folder(folder)
            self.update_playlist_view()
            
    def update_playlist_view(self):
        self.playlist_tree.delete(*self.playlist_tree.get_children())
        
        for track in self.playlist.tracks:
            self.playlist_tree.insert('', 'end', values=(
                track['title'],
                track['artist'],
                track['duration']
            ))
            
    def play_selected(self, event=None):
        selection = self.playlist_tree.selection()
        if not selection:
            return
            
        selected_idx = self.playlist_tree.index(selection[0])
        self.play_track(selected_idx)
        
    def play_track(self, index):
        if not 0 <= index < len(self.playlist.tracks):
            return
            
        # Stop current track if playing
        if self.playing:
            pygame.mixer.music.stop()
            
        self.current_track = index
        track = self.playlist.tracks[index]
        
        try:
            pygame.mixer.music.load(track['path'])
            pygame.mixer.music.play()
            self.playing = True
            self.play_button.config(text="⏸")
            
            # Update track info
            self.track_label.config(
                text=f"{track['title']} - {track['artist']}"
            )
            
            # Update track length
            audio = MP3(track['path'])
            self.track_length = audio.info.length
            self.progress_bar.config(to=self.track_length)
            
            # Start visualizer
            self.visualizer.start_visualization(track['path'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not play track: {str(e)}")
            
    def play_pause(self):
        if not self.current_track is None:
            if self.playing:
                pygame.mixer.music.pause()
                self.play_button.config(text="▶")
            else:
                pygame.mixer.music.unpause()
                self.play_button.config(text="⏸")
            self.playing = not self.playing
            
    def next_track(self):
        if self.current_track is not None:
            next_track = (self.current_track + 1) % len(self.playlist.tracks)
            self.play_track(next_track)
            
    def previous_track(self):
        if self.current_track is not None:
            prev_track = (self.current_track - 1) % len(self.playlist.tracks)
            self.play_track(prev_track)
            
    def seek(self, value):
        if self.playing:
            pygame.mixer.music.set_pos(float(value))
            
    def set_volume(self, value):
        volume = float(value) / 100
        pygame.mixer.music.set_volume(volume)
        
    def save_playlist(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.playlist.save_playlist(file_path)
            
    def load_playlist(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.playlist.load_playlist(file_path)
            self.update_playlist_view()
            
    def clear_playlist(self):
        if messagebox.askyesno("Confirm Clear", 
                             "Are you sure you want to clear the playlist?"):
            self.playlist.clear()
            self.update_playlist_view()
            
    def update_player(self):
        if self.playing:
            # Update progress bar
            current_time = pygame.mixer.music.get_pos() / 1000
            self.progress_var.set(current_time)
            
            # Update time label
            current_time_str = str(timedelta(seconds=int(current_time)))
            total_time_str = str(timedelta(seconds=int(self.track_length)))
            self.time_label.config(text=f"{current_time_str} / {total_time_str}")
            
            # Check if track ended
            if not pygame.mixer.music.get_busy():
                self.next_track()
                
        # Update visualizer
        if self.playing:
            self.visualizer.update()
            
        # Schedule next update
        self.root.after(100, self.update_player)
        
    def on_closing(self):
        pygame.mixer.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 