import cv2
from pyzbar.pyzbar import decode
import barcode
from barcode.writer import ImageWriter
import os
from PIL import Image

class BarcodeHandler:
    def __init__(self):
        self.barcode_dir = "barcodes"
        if not os.path.exists(self.barcode_dir):
            os.makedirs(self.barcode_dir)
            
    def scan_barcode(self):
        """Scan barcode using camera"""
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Find barcodes in frame
            barcodes = decode(frame)
            
            # Draw rectangle around barcode and show data
            for barcode in barcodes:
                x, y, w, h = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Get barcode data
                barcode_data = barcode.data.decode('utf-8')
                cv2.putText(frame, barcode_data, (x, y - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Release camera and return barcode data
                cap.release()
                cv2.destroyAllWindows()
                return barcode_data
                
            # Show frame
            cv2.imshow('Barcode Scanner', frame)
            
            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        # Release camera if no barcode found
        cap.release()
        cv2.destroyAllWindows()
        return None
        
    def generate_barcode(self, sku):
        """Generate barcode image for SKU"""
        try:
            # Create barcode
            EAN = barcode.get_barcode_class('code128')
            code = EAN(sku, writer=ImageWriter())
            
            # Save barcode image
            filename = os.path.join(self.barcode_dir, f"barcode_{sku}")
            code.save(filename)
            
            # Resize barcode image
            image_path = f"{filename}.png"
            img = Image.open(image_path)
            img = img.resize((300, 150), Image.Resampling.LANCZOS)
            img.save(image_path)
            
            return image_path
            
        except Exception as e:
            print(f"Error generating barcode: {str(e)}")
            return None
            
    def validate_barcode(self, barcode_data):
        """Validate barcode format"""
        # Add validation logic based on your barcode format
        return len(barcode_data) >= 6 