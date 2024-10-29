import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from scipy import signal
import pygame
import threading
import queue
import logging
from datetime import datetime

class AudioEffect:
    NORMALIZE = "normalize"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SPEED_UP = "speed_up"
    SLOW_DOWN = "slow_down"
    REVERSE = "reverse"
    ECHO = "echo"

class AudioProcessor:
    def __init__(self):
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: Optional[int] = None
        self.current_file: Optional[Path] = None
        self.log_file = Path("audio_processing.log")
        self.setup_logging()
        self.playback_thread: Optional[threading.Thread] = None
        self.playback_queue = queue.Queue()
        pygame.mixer.init()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_audio(self, file_path: str) -> bool:
        """Load audio file"""
        try:
            self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
            self.current_file = Path(file_path)
            logging.info(f"Loaded audio file: {file_path}")
            return True
        except Exception as e:
            logging.error(f"Error loading audio file: {e}")
            return False

    def save_audio(self, output_path: str, format: str = "wav") -> bool:
        """Save audio to file"""
        try:
            if self.audio_data is None:
                logging.error("No audio data to save")
                return False

            sf.write(output_path, self.audio_data, self.sample_rate)
            logging.info(f"Saved audio to: {output_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving audio: {e}")
            return False

    def apply_effect(self, effect: str, **kwargs) -> bool:
        """Apply audio effect"""
        if self.audio_data is None:
            logging.error("No audio data loaded")
            return False

        try:
            if effect == AudioEffect.NORMALIZE:
                self._normalize()
            elif effect == AudioEffect.FADE_IN:
                duration = kwargs.get('duration', 1.0)
                self._fade_in(duration)
            elif effect == AudioEffect.FADE_OUT:
                duration = kwargs.get('duration', 1.0)
                self._fade_out(duration)
            elif effect == AudioEffect.SPEED_UP:
                factor = kwargs.get('factor', 1.5)
                self._change_speed(factor)
            elif effect == AudioEffect.SLOW_DOWN:
                factor = kwargs.get('factor', 0.5)
                self._change_speed(factor)
            elif effect == AudioEffect.REVERSE:
                self._reverse()
            elif effect == AudioEffect.ECHO:
                delay = kwargs.get('delay', 0.3)
                decay = kwargs.get('decay', 0.5)
                self._add_echo(delay, decay)
            else:
                logging.error(f"Unknown effect: {effect}")
                return False

            logging.info(f"Applied effect: {effect}")
            return True
        except Exception as e:
            logging.error(f"Error applying effect {effect}: {e}")
            return False

    def _normalize(self):
        """Normalize audio amplitude"""
        self.audio_data = librosa.util.normalize(self.audio_data)

    def _fade_in(self, duration: float):
        """Apply fade in effect"""
        samples = int(duration * self.sample_rate)
        fade_curve = np.linspace(0, 1, samples)
        self.audio_data[:samples] *= fade_curve

    def _fade_out(self, duration: float):
        """Apply fade out effect"""
        samples = int(duration * self.sample_rate)
        fade_curve = np.linspace(1, 0, samples)
        self.audio_data[-samples:] *= fade_curve

    def _change_speed(self, factor: float):
        """Change audio speed"""
        self.audio_data = librosa.effects.time_stretch(self.audio_data, rate=factor)

    def _reverse(self):
        """Reverse audio"""
        self.audio_data = np.flip(self.audio_data)

    def _add_echo(self, delay: float, decay: float):
        """Add echo effect"""
        delay_samples = int(delay * self.sample_rate)
        echo_data = np.zeros_like(self.audio_data)
        echo_data[delay_samples:] = self.audio_data[:-delay_samples] * decay
        self.audio_data = self.audio_data + echo_data

    def trim_audio(self, start_time: float, end_time: float) -> bool:
        """Trim audio to specified time range"""
        try:
            if self.audio_data is None:
                logging.error("No audio data loaded")
                return False

            start_sample = int(start_time * self.sample_rate)
            end_sample = int(end_time * self.sample_rate)

            if start_sample < 0 or end_sample > len(self.audio_data):
                logging.error("Invalid trim range")
                return False

            self.audio_data = self.audio_data[start_sample:end_sample]
            logging.info(f"Trimmed audio: {start_time}s to {end_time}s")
            return True
        except Exception as e:
            logging.error(f"Error trimming audio: {e}")
            return False

    def get_duration(self) -> float:
        """Get audio duration in seconds"""
        if self.audio_data is None or self.sample_rate is None:
            return 0.0
        return len(self.audio_data) / self.sample_rate

    def plot_waveform(self, output_path: Optional[str] = None):
        """Plot audio waveform"""
        if self.audio_data is None:
            logging.error("No audio data loaded")
            return

        plt.figure(figsize=(12, 4))
        plt.plot(np.linspace(0, self.get_duration(), len(self.audio_data)), 
                self.audio_data)
        plt.title("Audio Waveform")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Amplitude")
        
        if output_path:
            plt.savefig(output_path)
            logging.info(f"Saved waveform plot to: {output_path}")
        else:
            plt.show()
        plt.close()

    def play_audio(self):
        """Play audio"""
        if self.audio_data is None:
            logging.error("No audio data loaded")
            return

        try:
            # Convert to 16-bit PCM
            audio_data_16bit = (self.audio_data * 32767).astype(np.int16)
            pygame.mixer.music.load(self.current_file)
            pygame.mixer.music.play()
            logging.info("Playing audio")
        except Exception as e:
            logging.error(f"Error playing audio: {e}")

    def stop_audio(self):
        """Stop audio playback"""
        pygame.mixer.music.stop()
        logging.info("Stopped audio playback")

def main():
    processor = AudioProcessor()
    
    while True:
        print("\nAudio Processing Tool")
        print("1. Load Audio")
        print("2. Apply Effect")
        print("3. Trim Audio")
        print("4. Save Audio")
        print("5. Plot Waveform")
        print("6. Play Audio")
        print("7. Stop Audio")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == "1":
            file_path = input("Enter audio file path: ")
            if processor.load_audio(file_path):
                print("Audio loaded successfully!")
                print(f"Duration: {processor.get_duration():.2f} seconds")
            else:
                print("Failed to load audio!")
        
        elif choice == "2":
            if processor.audio_data is None:
                print("Please load audio first!")
                continue
            
            print("\nAvailable effects:")
            print("1. Normalize")
            print("2. Fade In")
            print("3. Fade Out")
            print("4. Speed Up")
            print("5. Slow Down")
            print("6. Reverse")
            print("7. Echo")
            
            effect_choice = input("Choose effect (1-7): ")
            effects = {
                "1": AudioEffect.NORMALIZE,
                "2": AudioEffect.FADE_IN,
                "3": AudioEffect.FADE_OUT,
                "4": AudioEffect.SPEED_UP,
                "5": AudioEffect.SLOW_DOWN,
                "6": AudioEffect.REVERSE,
                "7": AudioEffect.ECHO
            }
            
            if effect_choice not in effects:
                print("Invalid effect choice!")
                continue
            
            effect = effects[effect_choice]
            kwargs = {}
            
            if effect in [AudioEffect.FADE_IN, AudioEffect.FADE_OUT]:
                duration = float(input("Enter duration (seconds): "))
                kwargs['duration'] = duration
            elif effect in [AudioEffect.SPEED_UP, AudioEffect.SLOW_DOWN]:
                factor = float(input("Enter speed factor: "))
                kwargs['factor'] = factor
            elif effect == AudioEffect.ECHO:
                delay = float(input("Enter delay (seconds): "))
                decay = float(input("Enter decay factor (0-1): "))
                kwargs['delay'] = delay
                kwargs['decay'] = decay
            
            if processor.apply_effect(effect, **kwargs):
                print("Effect applied successfully!")
            else:
                print("Failed to apply effect!")
        
        elif choice == "3":
            if processor.audio_data is None:
                print("Please load audio first!")
                continue
            
            duration = processor.get_duration()
            print(f"Current duration: {duration:.2f} seconds")
            start_time = float(input("Enter start time (seconds): "))
            end_time = float(input("Enter end time (seconds): "))
            
            if processor.trim_audio(start_time, end_time):
                print("Audio trimmed successfully!")
            else:
                print("Failed to trim audio!")
        
        elif choice == "4":
            if processor.audio_data is None:
                print("Please load audio first!")
                continue
            
            output_path = input("Enter output file path: ")
            if processor.save_audio(output_path):
                print("Audio saved successfully!")
            else:
                print("Failed to save audio!")
        
        elif choice == "5":
            if processor.audio_data is None:
                print("Please load audio first!")
                continue
            
            save = input("Save plot to file? (y/n): ").lower() == 'y'
            if save:
                output_path = input("Enter output file path: ")
                processor.plot_waveform(output_path)
                print("Waveform plot saved!")
            else:
                processor.plot_waveform()
        
        elif choice == "6":
            if processor.audio_data is None:
                print("Please load audio first!")
                continue
            
            processor.play_audio()
        
        elif choice == "7":
            processor.stop_audio()
        
        elif choice == "8":
            print("Thank you for using Audio Processing Tool!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 