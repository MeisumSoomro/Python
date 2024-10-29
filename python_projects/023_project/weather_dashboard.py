import PySimpleGUI as sg
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os
from typing import Dict, List, Optional
import io
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeatherDashboard:
    def __init__(self):
        self.api_key = "YOUR_API_KEY"  # Replace with your API key
        self.favorites_file = "favorites.json"
        self.favorites = self._load_favorites()
        self.current_city = None
        
    def add_favorite(self, city: str) -> None:
        if city not in self.favorites:
            self.favorites.append(city)
            self._save_favorites()

    def get_forecast(self, city: str) -> Optional[Dict]:
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return None

    def create_forecast_graph(self, forecast_data: Dict) -> Optional[bytes]:
        try:
            temps = []
            times = []
            
            for item in forecast_data['list'][:8]:  # Next 24 hours (3-hour intervals)
                temps.append(item['main']['temp'])
                times.append(datetime.fromtimestamp(item['dt']).strftime('%H:%M'))

            plt.figure(figsize=(10, 4))
            plt.plot(times, temps, marker='o')
            plt.title('24-Hour Temperature Forecast')
            plt.xlabel('Time')
            plt.ylabel('Temperature (°C)')
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Convert plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='PNG')
            plt.close()
            return buf.getvalue()
        except:
            return None

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def main():
    dashboard = WeatherDashboard()
    
    layout = [
        [sg.Text("Weather Dashboard", font=("Helvetica", 16))],
        [sg.Text("City:"), sg.Input(key="-CITY-"), sg.Button("Search")],
        [sg.Text("Current Weather:", font=("Helvetica", 12))],
        [sg.Text("Temperature: ", key="-TEMP-")],
        [sg.Text("Weather: ", key="-WEATHER-")],
        [sg.Text("Humidity: ", key="-HUMIDITY-")],
        [sg.Text("Forecast:", font=("Helvetica", 12))],
        [sg.Image(key="-GRAPH-")],
        [sg.Button("Add to Favorites"), sg.Button("View Favorites"), sg.Button("Exit")],
        [sg.Listbox(values=dashboard.favorites, size=(30, 5), key="-FAVORITES-", visible=False)]
    ]

    window = sg.Window("Weather Dashboard", layout, finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break
        
        if event == "Search":
            city = values["-CITY-"]
            if city:
                weather_data = dashboard.get_weather(city)
                forecast_data = dashboard.get_forecast(city)
                
                if weather_data and forecast_data:
                    window["-TEMP-"].update(f"Temperature: {weather_data['main']['temp']}°C")
                    window["-WEATHER-"].update(f"Weather: {weather_data['weather'][0]['description']}")
                    window["-HUMIDITY-"].update(f"Humidity: {weather_data['main']['humidity']}%")
                    
                    # Update forecast graph
                    graph_data = dashboard.create_forecast_graph(forecast_data)
                    if graph_data:
                        window["-GRAPH-"].update(data=graph_data)
                    
                    dashboard.current_city = city
                else:
                    sg.popup("Error fetching weather data!")

        if event == "Add to Favorites" and dashboard.current_city:
            dashboard.add_favorite(dashboard.current_city)
            window["-FAVORITES-"].update(values=dashboard.favorites)
            sg.popup(f"Added {dashboard.current_city} to favorites!")

        if event == "View Favorites":
            window["-FAVORITES-"].update(visible=not window["-FAVORITES-"].visible)

    window.close()

if __name__ == "__main__":
    main() 