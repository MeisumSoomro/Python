import unittest
import os
import tkinter as tk
from music_player import MusicPlayer
from playlist_manager import PlaylistManager

class TestMusicPlayer(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = MusicPlayer(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test files
        if os.path.exists('test_playlist.json'):
            os.remove('test_playlist.json')
            
    def test_playlist_manager(self):
        playlist = PlaylistManager()
        
        # Test adding files (requires test MP3 files)
        test_files = [
            'test_files/test1.mp3',
            'test_files/test2.mp3'
        ]
        
        if all(os.path.exists(f) for f in test_files):
            playlist.add_files(test_files)
            self.assertEqual(len(playlist.tracks), 2)
            
            # Test playlist save/load
            playlist.save_playlist('test_playlist.json')
            
            new_playlist = PlaylistManager()
            new_playlist.load_playlist('test_playlist.json')
            self.assertEqual(len(new_playlist.tracks), 2)
            
    def test_volume_control(self):
        # Test volume setting
        self.app.set_volume(50)
        self.assertEqual(self.app.volume_var.get(), 50)
        
        self.app.set_volume(0)
        self.assertEqual(self.app.volume_var.get(), 0)
        
        self.app.set_volume(100)
        self.assertEqual(self.app.volume_var.get(), 100)
        
if __name__ == '__main__':
    try:
        import pygame
        import mutagen
        import matplotlib
        import numpy
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 