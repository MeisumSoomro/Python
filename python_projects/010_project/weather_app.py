import requests
import json
from datetime import datetime

class WeatherApp:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city):
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Use Celsius
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            return self.format_weather_data(weather_data)
            
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather data: {str(e)}"
            
    def format_weather_data(self, data):
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'description': data['weather'][0]['description'].capitalize(),
            'timestamp': datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def display_weather(self, weather_data):
        if isinstance(weather_data, str):
            print(weather_data)
            return
            
        print("\nWeather Information:")
        print(f"Location: {weather_data['city']}, {weather_data['country']}")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Feels like: {weather_data['feels_like']}°C")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Wind Speed: {weather_data['wind_speed']} m/s")
        print(f"Conditions: {weather_data['description']}")
        print(f"Last Updated: {weather_data['timestamp']}")

def main():
    # Replace with your OpenWeatherMap API key
    API_KEY = "your_api_key_here"
    
    weather_app = WeatherApp(API_KEY)
    
    print("Welcome to Weather App!")
    
    while True:
        city = input("\nEnter city name (or 'quit' to exit): ")
        
        if city.lower() == 'quit':
            break
            
        weather_data = weather_app.get_weather(city)
        weather_app.display_weather(weather_data)
        
        if input("\nCheck another city? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main() 