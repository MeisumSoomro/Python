import tkinter as tk
from tkinter import ttk
import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import struct

class AudioVisualizer:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.canvas = None
        self.fig = None
        self.ax = None
        
    def show_window(self):
        """Create or show visualizer window"""
        if not self.window:
            self.window = tk.Toplevel(self.parent)
            self.window.title("Audio Visualizer")
            self.window.geometry("600x400")
            
            # Create matplotlib figure
            self.fig, self.ax = plt.subplots(figsize=(6, 4))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Initialize plot
            self.ax.set_ylim(-1, 1)
            self.ax.set_xlim(0, 1024)
            self.line, = self.ax.plot([], [])
            
            # Handle window closing
            self.window.protocol("WM_DELETE_WINDOW", self.hide_window)
        else:
            self.window.deiconify()
            
    def hide_window(self):
        """Hide visualizer window"""
        if self.window:
            self.window.withdraw()
            
    def start_visualization(self, audio_path):
        """Initialize visualization for a new track"""
        if self.window and self.window.winfo_exists():
            self.ax.clear()
            self.ax.set_ylim(-1, 1)
            self.ax.set_xlim(0, 1024)
            self.line, = self.ax.plot([], [])
            
    def update(self):
        """Update visualization"""
        if not (self.window and self.window.winfo_exists()):
            return
            
        try:
            # Get audio data from pygame
            array = pygame.sndarray.array(pygame.mixer.get_raw())
            # Convert to numpy array and normalize
            waveform = np.array(array) / 32768.0
            
            # Update plot
            if len(waveform) > 0:
                self.line.set_data(range(len(waveform[:1024])), waveform[:1024])
                self.canvas.draw()
                
        except Exception as e:
            print(f"Visualization error: {str(e)}") 