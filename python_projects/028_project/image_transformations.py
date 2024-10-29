from PIL import Image

class ImageTransformations:
    def rotate(self, image, degrees):
        """Rotate image by specified degrees"""
        return image.rotate(degrees, expand=True)
        
    def flip_horizontal(self, image):
        """Flip image horizontally"""
        return image.transpose(Image.FLIP_LEFT_RIGHT)
        
    def flip_vertical(self, image):
        """Flip image vertically"""
        return image.transpose(Image.FLIP_TOP_BOTTOM)
        
    def resize(self, image, width, height):
        """Resize image to specified dimensions"""
        return image.resize((width, height), Image.Resampling.LANCZOS)
        
    def crop(self, image, box):
        """Crop image to specified box (left, top, right, bottom)"""
        return image.crop(box)
        
    def scale(self, image, factor):
        """Scale image by factor"""
        width, height = image.size
        new_width = int(width * factor)
        new_height = int(height * factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS) 