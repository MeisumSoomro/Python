import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        
        # Image list and current index
        self.images = []
        self.current_index = -1
        
        # Create GUI elements
        self.create_menu()
        self.create_widgets()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Open Directory", command=self.open_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
    def create_widgets(self):
        # Navigation buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Button(button_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=5)
        
        # Image display area
        self.image_label = tk.Label(self.root)
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.images = [file_path]
            self.current_index = 0
            self.display_image()
            
    def open_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.images = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
            for file in os.listdir(directory):
                if file.lower().endswith(valid_extensions):
                    self.images.append(os.path.join(directory, file))
            
            if self.images:
                self.current_index = 0
                self.display_image()
            else:
                messagebox.showinfo("Info", "No valid images found in directory")
                
    def display_image(self):
        if 0 <= self.current_index < len(self.images):
            try:
                # Load and resize image
                image = Image.open(self.images[self.current_index])
                
                # Calculate resize dimensions while maintaining aspect ratio
                display_size = (800, 600)
                image.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Update display
                self.image_label.config(image=photo)
                self.image_label.image = photo  # Keep a reference
                
                # Update window title
                self.root.title(f"Image Viewer - {os.path.basename(self.images[self.current_index])}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {str(e)}")
                
    def next_image(self):
        if self.images and self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.display_image()
            
    def prev_image(self):
        if self.images and self.current_index > 0:
            self.current_index -= 1
            self.display_image()

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = ImageViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 