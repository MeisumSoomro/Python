import unittest
import os
import tkinter as tk
from PIL import Image
from image_editor import ImageEditor
from image_filters import ImageFilters
from image_transformations import ImageTransformations

class TestImageEditor(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = ImageEditor(self.root)
        
        # Create test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.test_image_path = 'test_image.png'
        self.test_image.save(self.test_image_path)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test files
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
            
    def test_filters(self):
        filters = ImageFilters()
        
        # Test brightness adjustment
        bright_image = filters.adjust_brightness(self.test_image, 1.5)
        self.assertEqual(bright_image.size, self.test_image.size)
        
        # Test grayscale conversion
        gray_image = filters.apply_grayscale(self.test_image)
        self.assertEqual(gray_image.mode, 'L')
        
        # Test blur filter
        blur_image = filters.apply_blur(self.test_image)
        self.assertEqual(blur_image.size, self.test_image.size)
        
    def test_transformations(self):
        transforms = ImageTransformations()
        
        # Test rotation
        rotated = transforms.rotate(self.test_image, 90)
        self.assertEqual(rotated.size, (100, 100))
        
        # Test flip
        flipped = transforms.flip_horizontal(self.test_image)
        self.assertEqual(flipped.size, self.test_image.size)
        
        # Test resize
        resized = transforms.resize(self.test_image, 50, 50)
        self.assertEqual(resized.size, (50, 50))
        
if __name__ == '__main__':
    try:
        import PIL
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 