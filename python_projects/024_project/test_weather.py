import unittest
import os
from datetime import datetime
import tkinter as tk
from weather_app import WeatherDashboard
from weather_api import WeatherAPI

class TestWeatherDashboard(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = WeatherDashboard(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test files
        if os.path.exists('weather_locations.json'):
            os.remove('weather_locations.json')
            
    def test_api_connection(self):
        # Test API connection with a known location
        try:
            weather_data = self.app.api.get_current_weather("London")
            self.assertIsNotNone(weather_data)
            self.assertIn('main', weather_data)
            self.assertIn('temp', weather_data['main'])
        except Exception as e:
            self.fail(f"API connection failed: {str(e)}")
            
    def test_location_save(self):
        # Test saving and loading locations
        test_location = "New York"
        self.app.location_var.set(test_location)
        self.app.save_current_location()
        
        # Reload locations
        saved_locations = self.app.load_saved_locations()
        self.assertIn(test_location, saved_locations)
        
    def test_unit_conversion(self):
        # Test temperature unit conversion
        api = WeatherAPI()
        
        # Test metric
        api.set_units('metric')
        self.assertEqual(api.units, 'metric')
        
        # Test imperial
        api.set_units('imperial')
        self.assertEqual(api.units, 'imperial')
        
        # Test invalid unit
        with self.assertRaises(ValueError):
            api.set_units('invalid_unit')
            
if __name__ == '__main__':
    try:
        import requests
        import PIL
        import matplotlib
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 