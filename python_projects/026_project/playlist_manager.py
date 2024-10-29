import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import json
from datetime import timedelta

class PlaylistManager:
    def __init__(self):
        self.tracks = []
        
    def add_files(self, file_paths):
        """Add individual music files to playlist"""
        for path in file_paths:
            if path.lower().endswith('.mp3'):
                track_info = self._get_track_info(path)
                if track_info:
                    self.tracks.append(track_info)
                    
    def add_folder(self, folder_path):
        """Add all music files from a folder"""
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.mp3'):
                    path = os.path.join(root, file)
                    track_info = self._get_track_info(path)
                    if track_info:
                        self.tracks.append(track_info)
                        
    def _get_track_info(self, file_path):
        """Extract track information from MP3 file"""
        try:
            audio = MP3(file_path)
            tags = EasyID3(file_path)
            
            # Get basic track info
            duration = str(timedelta(seconds=int(audio.info.length)))
            title = tags.get('title', [os.path.splitext(os.path.basename(file_path))[0]])[0]
            artist = tags.get('artist', ['Unknown Artist'])[0]
            
            return {
                'path': file_path,
                'title': title,
                'artist': artist,
                'duration': duration,
                'length': audio.info.length
            }
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return None
            
    def save_playlist(self, file_path):
        """Save playlist to JSON file"""
        try:
            playlist_data = []
            for track in self.tracks:
                # Store relative paths for portability
                track_copy = track.copy()
                track_copy['path'] = os.path.relpath(track['path'])
                playlist_data.append(track_copy)
                
            with open(file_path, 'w') as f:
                json.dump(playlist_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving playlist: {str(e)}")
            
    def load_playlist(self, file_path):
        """Load playlist from JSON file"""
        try:
            with open(file_path, 'r') as f:
                playlist_data = json.load(f)
                
            self.tracks = []
            playlist_dir = os.path.dirname(file_path)
            
            for track in playlist_data:
                # Convert relative paths to absolute
                track['path'] = os.path.join(playlist_dir, track['path'])
                if os.path.exists(track['path']):
                    self.tracks.append(track)
                    
        except Exception as e:
            print(f"Error loading playlist: {str(e)}")
            
    def clear(self):
        """Clear the playlist"""
        self.tracks = [] 