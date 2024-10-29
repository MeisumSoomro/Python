import PySimpleGUI as sg
import pygame
import os
from mutagen.mp3 import MP3
from typing import List, Optional, Dict
import json
import time
from threading import Thread

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_track: Optional[str] = None
        self.playing: bool = False
        self.paused: bool = False
        self.playlist: List[Dict] = []
        self.current_index: int = 0
        self.volume: float = 0.5
        pygame.mixer.music.set_volume(self.volume)
        
        # Load saved playlist if exists
        self.playlist_file = "playlist.json"
        self._load_playlist()

    def _load_playlist(self) -> None:
        if os.path.exists(self.playlist_file):
            try:
                with open(self.playlist_file, 'r') as f:
                    self.playlist = json.load(f)
            except:
                self.playlist = []

    def _save_playlist(self) -> None:
        with open(self.playlist_file, 'w') as f:
            json.dump(self.playlist, f)

    def add_track(self, filepath: str) -> None:
        if os.path.exists(filepath):
            track_info = self._get_track_info(filepath)
            self.playlist.append(track_info)
            self._save_playlist()

    def _get_track_info(self, filepath: str) -> Dict:
        audio = MP3(filepath)
        return {
            'path': filepath,
            'title': os.path.basename(filepath),
            'duration': int(audio.info.length),
            'duration_str': time.strftime('%M:%S', time.gmtime(audio.info.length))
        }

    def play(self, index: Optional[int] = None) -> None:
        if not self.playlist:
            return

        if index is not None:
            self.current_index = index
        
        self.current_track = self.playlist[self.current_index]['path']
        pygame.mixer.music.load(self.current_track)
        pygame.mixer.music.play()
        self.playing = True
        self.paused = False

    def pause(self) -> None:
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False

    def next_track(self) -> None:
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def prev_track(self) -> None:
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

def create_layout():
    return [
        [sg.Text("Music Player", font=("Helvetica", 16))],
        [sg.Button("Add Track"), sg.Button("Remove Track")],
        [sg.Listbox(
            values=[],
            size=(50, 10),
            key="-PLAYLIST-",
            enable_events=True
        )],
        [sg.Text("Now Playing:", key="-NOW-PLAYING-")],
        [
            sg.Button("⏮", key="-PREV-"),
            sg.Button("⏯", key="-PLAY-PAUSE-"),
            sg.Button("⏹", key="-STOP-"),
            sg.Button("⏭", key="-NEXT-")
        ],
        [
            sg.Text("Volume:"),
            sg.Slider(
                range=(0, 100),
                default_value=50,
                orientation='h',
                key="-VOLUME-",
                enable_events=True
            )
        ],
        [sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS-')],
        [sg.Button("Exit")]
    ]

def update_progress(window, player):
    while True:
        if player.playing and not player.paused:
            try:
                current_pos = pygame.mixer.music.get_pos() / 1000
                total_length = player.playlist[player.current_index]['duration']
                progress = (current_pos / total_length) * 100
                window.write_event_value('-UPDATE-PROGRESS-', progress)
            except:
                pass
        time.sleep(0.1)

def main():
    player = MusicPlayer()
    window = sg.Window("Music Player", create_layout(), finalize=True)
    
    # Start progress update thread
    progress_thread = Thread(target=update_progress, args=(window, player), daemon=True)
    progress_thread.start()

    while True:
        event, values = window.read(timeout=100)
        
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "Add Track":
            files = sg.popup_get_file(
                "Choose tracks to add",
                multiple_files=True,
                file_types=(("MP3 Files", "*.mp3"),)
            )
            if files:
                if isinstance(files, str):
                    files = [files]
                for file in files:
                    player.add_track(file)
                window["-PLAYLIST-"].update([track['title'] for track in player.playlist])

        if event == "-PLAY-PAUSE-":
            if not player.playing:
                selected_rows = values["-PLAYLIST-"]
                if selected_rows:
                    index = player.playlist.index(
                        next(track for track in player.playlist 
                            if track['title'] == selected_rows[0])
                    )
                    player.play(index)
                elif player.playlist:
                    player.play()
            else:
                player.pause()

        if event == "-STOP-":
            player.stop()

        if event == "-NEXT-":
            player.next_track()

        if event == "-PREV-":
            player.prev_track()

        if event == "-VOLUME-":
            player.set_volume(values["-VOLUME-"] / 100)

        if event == "-UPDATE-PROGRESS-":
            window["-PROGRESS-"].update(values[event])

        # Update now playing text
        if player.playing and player.current_index < len(player.playlist):
            current_track = player.playlist[player.current_index]
            window["-NOW-PLAYING-"].update(
                f"Now Playing: {current_track['title']} ({current_track['duration_str']})"
            )

    window.close()

if __name__ == "__main__":
    main() 