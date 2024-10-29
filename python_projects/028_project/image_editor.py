import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os
from image_filters import ImageFilters
from image_transformations import ImageTransformations

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        
        # Initialize variables
        self.original_image = None
        self.current_image = None
        self.image_path = None
        self.undo_stack = []
        self.redo_stack = []
        
        # Initialize handlers
        self.filters = ImageFilters()
        self.transforms = ImageTransformations()
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Save As", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset", command=self.reset_image)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel with tools
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Basic adjustments
        adjust_frame = ttk.LabelFrame(left_frame, text="Adjustments")
        adjust_frame.pack(fill=tk.X, pady=5)
        
        # Brightness
        ttk.Label(adjust_frame, text="Brightness:").pack(anchor='w')
        self.brightness_var = tk.DoubleVar(value=1.0)
        brightness_scale = ttk.Scale(adjust_frame, from_=0.0, to=2.0,
                                   variable=self.brightness_var,
                                   command=self.adjust_brightness)
        brightness_scale.pack(fill=tk.X, padx=5)
        
        # Contrast
        ttk.Label(adjust_frame, text="Contrast:").pack(anchor='w')
        self.contrast_var = tk.DoubleVar(value=1.0)
        contrast_scale = ttk.Scale(adjust_frame, from_=0.0, to=2.0,
                                 variable=self.contrast_var,
                                 command=self.adjust_contrast)
        contrast_scale.pack(fill=tk.X, padx=5)
        
        # Filters
        filter_frame = ttk.LabelFrame(left_frame, text="Filters")
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(filter_frame, text="Blur", 
                  command=self.apply_blur).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(filter_frame, text="Sharpen", 
                  command=self.apply_sharpen).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(filter_frame, text="Grayscale", 
                  command=self.apply_grayscale).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(filter_frame, text="Edge Enhance", 
                  command=self.apply_edge_enhance).pack(fill=tk.X, padx=5, pady=2)
        
        # Transformations
        transform_frame = ttk.LabelFrame(left_frame, text="Transform")
        transform_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(transform_frame, text="Rotate Left", 
                  command=lambda: self.rotate_image(-90)
                  ).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(transform_frame, text="Rotate Right", 
                  command=lambda: self.rotate_image(90)
                  ).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(transform_frame, text="Flip Horizontal", 
                  command=self.flip_horizontal).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(transform_frame, text="Flip Vertical", 
                  command=self.flip_vertical).pack(fill=tk.X, padx=5, pady=2)
        
        # Right panel with image
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Canvas for image
        self.canvas = tk.Canvas(right_frame, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.canvas.create_text(
            self.canvas.winfo_reqwidth() // 2,
            self.canvas.winfo_reqheight() // 2,
            text="Open an image to begin editing",
            fill="white",
            font=('Arial', 14)
        )
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                self.undo_stack = []
                self.redo_stack = []
                self.show_image()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {str(e)}")
                
    def save_image(self):
        if not self.current_image:
            return
            
        if self.image_path:
            try:
                self.current_image.save(self.image_path)
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
        else:
            self.save_image_as()
            
    def save_image_as(self):
        if not self.current_image:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                self.current_image.save(file_path)
                self.image_path = file_path
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
                
    def show_image(self):
        if not self.current_image:
            return
            
        # Resize image to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        image_width, image_height = self.current_image.size
        ratio = min(canvas_width/image_width, canvas_height/image_height)
        
        new_width = int(image_width * ratio)
        new_height = int(image_height * ratio)
        
        resized_image = self.current_image.resize((new_width, new_height), 
                                                Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(resized_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width//2,
            canvas_height//2,
            image=self.photo,
            anchor=tk.CENTER
        )
        
    def push_undo(self):
        """Save current state to undo stack"""
        self.undo_stack.append(self.current_image.copy())
        self.redo_stack.clear()
        
    def undo(self):
        if not self.undo_stack:
            return
            
        self.redo_stack.append(self.current_image.copy())
        self.current_image = self.undo_stack.pop()
        self.show_image()
        
    def redo(self):
        if not self.redo_stack:
            return
            
        self.undo_stack.append(self.current_image.copy())
        self.current_image = self.redo_stack.pop()
        self.show_image()
        
    def reset_image(self):
        if not self.original_image:
            return
            
        self.push_undo()
        self.current_image = self.original_image.copy()
        self.show_image()
        
        # Reset adjustment values
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        
    def adjust_brightness(self, value):
        if not self.current_image:
            return
            
        self.push_undo()
        value = float(value)
        self.current_image = self.filters.adjust_brightness(
            self.current_image, value
        )
        self.show_image()
        
    def adjust_contrast(self, value):
        if not self.current_image:
            return
            
        self.push_undo()
        value = float(value)
        self.current_image = self.filters.adjust_contrast(
            self.current_image, value
        )
        self.show_image()
        
    def apply_blur(self):
        if not self.current_image:
            return
            
        self.push_undo()
        self.current_image = self.filters.apply_blur(self.current_image)
        self.show_image()
        
    def apply_sharpen(self):
        if not self.current_image:
            return
            
        self.push_undo()
        self.current_image = self.filters.apply_sharpen(self.current_image)
        self.show_image()
        
    def apply_grayscale(self):
        if not self.current_image:
            return
            
        self.push_undo()
        self.current_image = self.filters.apply_grayscale(self.current_image)
        self.show_image()
        
    def apply_edge_enhance(self):
        if not self.current_image:
            return
            
        self.push_undo()
        self.current_image = self.filters.apply_edge_enhance(self.current_image)
        self.show_image()
        
    def rotate_image(self, degrees):
        if not self.current_image:
            return
            
        self.push_undo()
        self.current_image = self.transforms.rotate(self.current_image, degrees)
        self.show_image()
        
    def flip_horizontal(self):
        if not self.current_image:
            return
            
        self.push_undo()
        self.current_image = self.transforms.flip_horizontal(self.current_image)
        self.show_image()
        
    def flip_vertical(self):
        if not self.current_image:
            return
            
        self.push_undo()
        self.current_image = self.transforms.flip_vertical(self.current_image)
        self.show_image()
        
    def zoom_in(self):
        # TODO: Implement zoom in
        pass
        
    def zoom_out(self):
        # TODO: Implement zoom out
        pass
        
    def fit_to_window(self):
        if self.current_image:
            self.show_image()

def main():
    root = tk.Tk()
    root.geometry("1200x800")
    app = ImageEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main() 