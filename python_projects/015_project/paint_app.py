import tkinter as tk
from tkinter import colorchooser, messagebox
import json

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint App")
        
        # Drawing settings
        self.current_color = "black"
        self.brush_size = 2
        self.drawing = False
        
        # Create GUI elements
        self.create_widgets()
        self.create_canvas()
        self.create_bindings()
        
        # Drawing history for undo/redo
        self.history = []
        self.current_drawing = []
        self.redo_stack = []
        
    def create_widgets(self):
        # Toolbar
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Color button
        tk.Button(toolbar, text="Color", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        
        # Brush size slider
        tk.Label(toolbar, text="Brush Size:").pack(side=tk.LEFT, padx=5)
        self.size_scale = tk.Scale(toolbar, from_=1, to=50, orient=tk.HORIZONTAL)
        self.size_scale.set(2)
        self.size_scale.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        tk.Button(toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        
        # Undo/Redo buttons
        tk.Button(toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=5)
        
        # Save/Load buttons
        tk.Button(toolbar, text="Save", command=self.save_drawing).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Load", command=self.load_drawing).pack(side=tk.LEFT, padx=5)
        
    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
    def create_bindings(self):
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Color")[1]
        if color:
            self.current_color = color
            
    def start_drawing(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        self.current_drawing = []
        
    def draw(self, event):
        if self.drawing:
            brush_size = self.size_scale.get()
            line = self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                fill=self.current_color, width=brush_size,
                capstyle=tk.ROUND, smooth=True
            )
            self.current_drawing.append({
                'type': 'line',
                'coords': [self.last_x, self.last_y, event.x, event.y],
                'color': self.current_color,
                'width': brush_size,
                'id': line
            })
            self.last_x = event.x
            self.last_y = event.y
            
    def stop_drawing(self, event):
        if self.drawing and self.current_drawing:
            self.history.append(self.current_drawing)
            self.redo_stack.clear()
        self.drawing = False
        
    def clear_canvas(self):
        self.canvas.delete("all")
        self.history.clear()
        self.redo_stack.clear()
        
    def undo(self):
        if self.history:
            strokes = self.history.pop()
            self.redo_stack.append(strokes)
            for stroke in strokes:
                self.canvas.delete(stroke['id'])
                
    def redo(self):
        if self.redo_stack:
            strokes = self.redo_stack.pop()
            new_strokes = []
            for stroke in strokes:
                line = self.canvas.create_line(
                    stroke['coords'],
                    fill=stroke['color'],
                    width=stroke['width'],
                    capstyle=tk.ROUND,
                    smooth=True
                )
                new_strokes.append({**stroke, 'id': line})
            self.history.append(new_strokes)
            
    def save_drawing(self):
        try:
            drawing_data = []
            for strokes in self.history:
                stroke_data = []
                for stroke in strokes:
                    stroke_data.append({
                        'coords': stroke['coords'],
                        'color': stroke['color'],
                        'width': stroke['width']
                    })
                drawing_data.append(stroke_data)
                
            with open('drawing.json', 'w') as f:
                json.dump(drawing_data, f)
            messagebox.showinfo("Success", "Drawing saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save drawing: {str(e)}")
            
    def load_drawing(self):
        try:
            with open('drawing.json', 'r') as f:
                drawing_data = json.load(f)
                
            self.clear_canvas()
            for strokes in drawing_data:
                new_strokes = []
                for stroke in strokes:
                    line = self.canvas.create_line(
                        stroke['coords'],
                        fill=stroke['color'],
                        width=stroke['width'],
                        capstyle=tk.ROUND,
                        smooth=True
                    )
                    new_strokes.append({**stroke, 'id': line})
                self.history.append(new_strokes)
                
            messagebox.showinfo("Success", "Drawing loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load drawing: {str(e)}")

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = PaintApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 