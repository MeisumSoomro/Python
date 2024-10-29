import PySimpleGUI as sg
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
from typing import Optional, Tuple, Dict
from enum import Enum

class FilterType(Enum):
    BLUR = "Blur"
    SHARPEN = "Sharpen"
    CONTOUR = "Contour"
    EMBOSS = "Emboss"
    EDGE_ENHANCE = "Edge Enhance"

class ImageEditor:
    def __init__(self):
        self.image: Optional[Image.Image] = None
        self.original_image: Optional[Image.Image] = None
        self.current_file: Optional[str] = None
        self.undo_stack: list = []
        self.redo_stack: list = []
        
    def load_image(self, filepath: str) -> bool:
        try:
            self.image = Image.open(filepath)
            self.original_image = self.image.copy()
            self.current_file = filepath
            self._push_to_undo_stack()
            return True
        except Exception as e:
            sg.popup_error(f"Error loading image: {str(e)}")
            return False
    
    def save_image(self, filepath: str) -> bool:
        try:
            if self.image:
                self.image.save(filepath)
                return True
            return False
        except Exception as e:
            sg.popup_error(f"Error saving image: {str(e)}")
            return False
    
    def _push_to_undo_stack(self):
        if self.image:
            self.undo_stack.append(self.image.copy())
            self.redo_stack.clear()
    
    def undo(self) -> bool:
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.image = self.undo_stack[-1].copy()
            return True
        return False
    
    def redo(self) -> bool:
        if self.redo_stack:
            self.undo_stack.append(self.redo_stack.pop())
            self.image = self.undo_stack[-1].copy()
            return True
        return False
    
    def apply_filter(self, filter_type: FilterType):
        if not self.image:
            return False
            
        self._push_to_undo_stack()
        try:
            if filter_type == FilterType.BLUR:
                self.image = self.image.filter(ImageFilter.BLUR)
            elif filter_type == FilterType.SHARPEN:
                self.image = self.image.filter(ImageFilter.SHARPEN)
            elif filter_type == FilterType.CONTOUR:
                self.image = self.image.filter(ImageFilter.CONTOUR)
            elif filter_type == FilterType.EMBOSS:
                self.image = self.image.filter(ImageFilter.EMBOSS)
            elif filter_type == FilterType.EDGE_ENHANCE:
                self.image = self.image.filter(ImageFilter.EDGE_ENHANCE)
            return True
        except:
            return False
    
    def adjust_brightness(self, factor: float) -> bool:
        if not self.image:
            return False
        
        self._push_to_undo_stack()
        try:
            enhancer = ImageEnhance.Brightness(self.image)
            self.image = enhancer.enhance(factor)
            return True
        except:
            return False
    
    def adjust_contrast(self, factor: float) -> bool:
        if not self.image:
            return False
        
        self._push_to_undo_stack()
        try:
            enhancer = ImageEnhance.Contrast(self.image)
            self.image = enhancer.enhance(factor)
            return True
        except:
            return False
    
    def rotate_image(self, degrees: float) -> bool:
        if not self.image:
            return False
        
        self._push_to_undo_stack()
        try:
            self.image = self.image.rotate(degrees, expand=True)
            return True
        except:
            return False
    
    def resize_image(self, size: Tuple[int, int]) -> bool:
        if not self.image:
            return False
        
        self._push_to_undo_stack()
        try:
            self.image = self.image.resize(size, Image.LANCZOS)
            return True
        except:
            return False
    
    def get_image_data(self) -> Optional[bytes]:
        if not self.image:
            return None
        
        bio = io.BytesIO()
        self.image.save(bio, format="PNG")
        return bio.getvalue()

def create_layout():
    filters_frame = [
        [sg.Button(filter_type.value) for filter_type in FilterType]
    ]
    
    adjustments_frame = [
        [
            sg.Text("Brightness:"),
            sg.Slider(
                range=(0.0, 2.0),
                default_value=1.0,
                resolution=0.1,
                orientation='h',
                key="-BRIGHTNESS-",
                enable_events=True
            )
        ],
        [
            sg.Text("Contrast:"),
            sg.Slider(
                range=(0.0, 2.0),
                default_value=1.0,
                resolution=0.1,
                orientation='h',
                key="-CONTRAST-",
                enable_events=True
            )
        ]
    ]
    
    transform_frame = [
        [
            sg.Button("Rotate Left"),
            sg.Button("Rotate Right"),
            sg.Button("Resize")
        ]
    ]
    
    return [
        [sg.Menu([['File', ['Open', 'Save', 'Save As', '---', 'Exit']],
                  ['Edit', ['Undo', 'Redo', 'Reset']]])],
        [sg.Image(key="-IMAGE-", size=(400, 400))],
        [sg.Frame("Filters", filters_frame)],
        [sg.Frame("Adjustments", adjustments_frame)],
        [sg.Frame("Transform", transform_frame)]
    ]

def main():
    editor = ImageEditor()
    window = sg.Window("Image Editor", create_layout(), resizable=True, finalize=True)
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
            
        if event == 'Open':
            filepath = sg.popup_get_file('Open Image', file_types=(("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),))
            if filepath:
                if editor.load_image(filepath):
                    window["-IMAGE-"].update(data=editor.get_image_data())
        
        if event == 'Save' and editor.current_file:
            editor.save_image(editor.current_file)
            
        if event == 'Save As':
            filepath = sg.popup_get_file('Save Image As', save_as=True, file_types=(("PNG", "*.png"),))
            if filepath:
                editor.save_image(filepath)
        
        if event == 'Undo':
            if editor.undo():
                window["-IMAGE-"].update(data=editor.get_image_data())
                
        if event == 'Redo':
            if editor.redo():
                window["-IMAGE-"].update(data=editor.get_image_data())
        
        if event == 'Reset' and editor.original_image:
            editor.image = editor.original_image.copy()
            editor._push_to_undo_stack()
            window["-IMAGE-"].update(data=editor.get_image_data())
        
        # Handle filters
        if event in [filter_type.value for filter_type in FilterType]:
            filter_type = FilterType(event)
            if editor.apply_filter(filter_type):
                window["-IMAGE-"].update(data=editor.get_image_data())
        
        # Handle adjustments
        if event == "-BRIGHTNESS-":
            if editor.adjust_brightness(values["-BRIGHTNESS-"]):
                window["-IMAGE-"].update(data=editor.get_image_data())
                
        if event == "-CONTRAST-":
            if editor.adjust_contrast(values["-CONTRAST-"]):
                window["-IMAGE-"].update(data=editor.get_image_data())
        
        # Handle transforms
        if event == "Rotate Left":
            if editor.rotate_image(90):
                window["-IMAGE-"].update(data=editor.get_image_data())
                
        if event == "Rotate Right":
            if editor.rotate_image(-90):
                window["-IMAGE-"].update(data=editor.get_image_data())
                
        if event == "Resize":
            current_size = editor.image.size if editor.image else (0, 0)
            layout = [
                [sg.Text("Width:"), sg.Input(current_size[0], key="-WIDTH-")],
                [sg.Text("Height:"), sg.Input(current_size[1], key="-HEIGHT-")],
                [sg.Button("OK"), sg.Button("Cancel")]
            ]
            resize_window = sg.Window("Resize Image", layout)
            resize_event, resize_values = resize_window.read(close=True)
            
            if resize_event == "OK":
                try:
                    new_size = (
                        int(resize_values["-WIDTH-"]),
                        int(resize_values["-HEIGHT-"])
                    )
                    if editor.resize_image(new_size):
                        window["-IMAGE-"].update(data=editor.get_image_data())
                except ValueError:
                    sg.popup_error("Please enter valid numbers for width and height")
    
    window.close()

if __name__ == "__main__":
    main() 