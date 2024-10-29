from PIL import Image, ImageEnhance, ImageFilter

class ImageFilters:
    def adjust_brightness(self, image, factor):
        """Adjust image brightness"""
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
        
    def adjust_contrast(self, image, factor):
        """Adjust image contrast"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
        
    def adjust_color(self, image, factor):
        """Adjust image color saturation"""
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)
        
    def adjust_sharpness(self, image, factor):
        """Adjust image sharpness"""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
        
    def apply_blur(self, image):
        """Apply Gaussian blur filter"""
        return image.filter(ImageFilter.GaussianBlur(radius=2))
        
    def apply_sharpen(self, image):
        """Apply sharpening filter"""
        return image.filter(ImageFilter.SHARPEN)
        
    def apply_grayscale(self, image):
        """Convert image to grayscale"""
        return image.convert('L')
        
    def apply_edge_enhance(self, image):
        """Apply edge enhancement filter"""
        return image.filter(ImageFilter.EDGE_ENHANCE)
        
    def apply_emboss(self, image):
        """Apply emboss filter"""
        return image.filter(ImageFilter.EMBOSS)
        
    def apply_find_edges(self, image):
        """Apply edge detection filter"""
        return image.filter(ImageFilter.FIND_EDGES)
        
    def apply_contour(self, image):
        """Apply contour filter"""
        return image.filter(ImageFilter.CONTOUR)
        
    def apply_smooth(self, image):
        """Apply smoothing filter"""
        return image.filter(ImageFilter.SMOOTH)
        
    def apply_detail(self, image):
        """Apply detail enhancement filter"""
        return image.filter(ImageFilter.DETAIL) 