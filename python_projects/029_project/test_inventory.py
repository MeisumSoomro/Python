import unittest
import os
import tkinter as tk
from inventory_manager import InventoryManager
from inventory_database import InventoryDatabase
from barcode_handler import BarcodeHandler
from report_generator import ReportGenerator

class TestInventorySystem(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = InventoryManager(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test files
        test_files = [
            'inventory.db',
            'test_inventory.json',
            'test_report.xlsx'
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                
    def test_database_operations(self):
        db = InventoryDatabase()
        
        # Test adding product
        test_product = {
            'sku': 'TEST001',
            'name': 'Test Product',
            'category': 'Electronics',
            'quantity': 10,
            'price': 99.99,
            'threshold': 5,
            'description': 'Test description',
            'created_date': '2024-01-01 12:00'
        }
        
        db.add_product(test_product)
        products = db.get_all_products()
        
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], 'Test Product')
        
        # Test updating product
        products[0]['quantity'] = 5
        db.update_product(products[0])
        
        updated = db.get_product(products[0]['id'])
        self.assertEqual(updated['quantity'], 5)
        
        # Test low stock alert
        low_stock = db.get_low_stock_products()
        self.assertEqual(len(low_stock), 1)
        
        db.close()
        
    def test_barcode_handler(self):
        handler = BarcodeHandler()
        
        # Test barcode generation
        sku = "TEST001"
        barcode_path = handler.generate_barcode(sku)
        
        self.assertIsNotNone(barcode_path)
        self.assertTrue(os.path.exists(barcode_path))
        
        # Test barcode validation
        self.assertTrue(handler.validate_barcode(sku))
        self.assertFalse(handler.validate_barcode("123"))
        
    def test_report_generator(self):
        generator = ReportGenerator()
        
        # Test stock report generation
        products = [{
            'sku': 'TEST001',
            'name': 'Test Product',
            'category': 'Electronics',
            'quantity': 10,
            'threshold': 5
        }]
        
        generator.generate_stock_report(products)
        report_files = os.listdir(generator.report_dir)
        self.assertTrue(any(f.startswith('stock_report_') for f in report_files))
        
if __name__ == '__main__':
    try:
        import cv2
        import pyzbar
        import barcode
        import pandas
        import matplotlib
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 