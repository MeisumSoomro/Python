import requests
import os
from datetime import datetime

class WeatherAPI:
    def __init__(self):
        # Get API key from environment variable or use a default one
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.units = "metric"  # Celsius by default
        
    def get_current_weather(self, location):
        """Get current weather for a location"""
        url = f"{self.base_url}/weather"
        params = {
            'q': location,
            'appid': self.api_key,
            'units': self.units
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = response.json().get('message', 'Unknown error')
            raise Exception(f"Weather API Error: {error_msg}")
            
    def get_forecast(self, location):
        """Get 5-day forecast for a location"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': location,
            'appid': self.api_key,
            'units': self.units
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = response.json().get('message', 'Unknown error')
            raise Exception(f"Weather API Error: {error_msg}")
            
    def set_units(self, unit_system):
        """Set temperature unit system (metric/imperial)"""
        if unit_system in ['metric', 'imperial']:
            self.units = unit_system
        else:
            raise ValueError("Unit system must be 'metric' or 'imperial'") 