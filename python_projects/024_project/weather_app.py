import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import json
import os
from weather_api import WeatherAPI
from PIL import Image, ImageTk
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeatherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Dashboard")
        
        # Initialize API
        self.api = WeatherAPI()
        
        # Load saved locations
        self.saved_locations = self.load_saved_locations()
        self.current_weather = None
        self.forecast_data = None
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Load last location if available
        if self.saved_locations:
            self.search_location(self.saved_locations[0])
            
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Location", command=self.save_current_location)
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Temperature Graph", command=self.show_temp_graph)
        view_menu.add_command(label="Forecast Details", command=self.show_forecast_details)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        self.location_var = tk.StringVar()
        location_entry = ttk.Entry(search_frame, textvariable=self.location_var)
        location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(search_frame, text="Search", 
                  command=lambda: self.search_location(self.location_var.get())
                  ).pack(side=tk.LEFT)
        
        # Saved locations
        if self.saved_locations:
            locations_frame = ttk.LabelFrame(main_frame, text="Saved Locations")
            locations_frame.pack(fill=tk.X, pady=5)
            
            for location in self.saved_locations:
                ttk.Button(locations_frame, text=location,
                          command=lambda l=location: self.search_location(l)
                          ).pack(side=tk.LEFT, padx=2)
        
        # Current weather frame
        self.current_frame = ttk.LabelFrame(main_frame, text="Current Weather")
        self.current_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Weather icon and basic info
        self.weather_icon_label = ttk.Label(self.current_frame)
        self.weather_icon_label.pack(pady=5)
        
        self.temp_label = ttk.Label(self.current_frame, 
                                  text="Temperature: --°C", font=('Arial', 14))
        self.temp_label.pack(pady=2)
        
        self.desc_label = ttk.Label(self.current_frame, 
                                  text="Description: --", font=('Arial', 12))
        self.desc_label.pack(pady=2)
        
        self.humidity_label = ttk.Label(self.current_frame, 
                                      text="Humidity: --%")
        self.humidity_label.pack(pady=2)
        
        self.wind_label = ttk.Label(self.current_frame, 
                                  text="Wind: -- m/s")
        self.wind_label.pack(pady=2)
        
        # Forecast frame
        forecast_frame = ttk.LabelFrame(main_frame, text="5-Day Forecast")
        forecast_frame.pack(fill=tk.X, pady=5)
        
        # Create forecast day frames
        self.forecast_frames = []
        for i in range(5):
            day_frame = ttk.Frame(forecast_frame)
            day_frame.pack(side=tk.LEFT, expand=True, padx=2)
            
            ttk.Label(day_frame, text="--").pack()  # Day
            ttk.Label(day_frame, text="--°C").pack()  # Temp
            ttk.Label(day_frame, text="--").pack()  # Description
            
            self.forecast_frames.append(day_frame)
            
    def search_location(self, location):
        if not location:
            return
            
        try:
            # Get current weather
            self.current_weather = self.api.get_current_weather(location)
            self.update_current_weather()
            
            # Get forecast
            self.forecast_data = self.api.get_forecast(location)
            self.update_forecast()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def update_current_weather(self):
        if not self.current_weather:
            return
            
        # Update weather icon
        icon_url = self.current_weather['weather'][0]['icon']
        self.load_weather_icon(icon_url)
        
        # Update labels
        temp = self.current_weather['main']['temp']
        self.temp_label.config(
            text=f"Temperature: {temp}°C"
        )
        
        desc = self.current_weather['weather'][0]['description'].capitalize()
        self.desc_label.config(text=f"Description: {desc}")
        
        humidity = self.current_weather['main']['humidity']
        self.humidity_label.config(text=f"Humidity: {humidity}%")
        
        wind = self.current_weather['wind']['speed']
        self.wind_label.config(text=f"Wind: {wind} m/s")
        
    def update_forecast(self):
        if not self.forecast_data:
            return
            
        # Get daily forecasts (every 24 hours)
        daily_forecasts = self.forecast_data['list'][::8]
        
        for frame, forecast in zip(self.forecast_frames, daily_forecasts):
            date = datetime.fromtimestamp(forecast['dt'])
            day = date.strftime("%A")
            temp = forecast['main']['temp']
            desc = forecast['weather'][0]['description'].capitalize()
            
            # Update frame labels
            frame.winfo_children()[0].config(text=day)
            frame.winfo_children()[1].config(text=f"{temp}°C")
            frame.winfo_children()[2].config(text=desc)
            
    def load_weather_icon(self, icon_code):
        try:
            icon_url = f"http://openweathermap.org/img/w/{icon_code}.png"
            response = requests.get(icon_url)
            img_data = Image.open(BytesIO(response.content))
            img = ImageTk.PhotoImage(img_data)
            self.weather_icon_label.config(image=img)
            self.weather_icon_label.image = img
        except Exception as e:
            print(f"Error loading weather icon: {e}")
            
    def save_current_location(self):
        location = self.location_var.get()
        if location and location not in self.saved_locations:
            self.saved_locations.append(location)
            self.save_locations()
            messagebox.showinfo("Success", "Location saved!")
            
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        
        ttk.Label(settings_window, text="Temperature Unit:").pack(pady=5)
        unit_var = tk.StringVar(value="metric")
        ttk.Radiobutton(settings_window, text="Celsius", 
                       variable=unit_var, value="metric").pack()
        ttk.Radiobutton(settings_window, text="Fahrenheit", 
                       variable=unit_var, value="imperial").pack()
        
        def save_settings():
            # Implement settings save
            settings_window.destroy()
            
        ttk.Button(settings_window, text="Save", 
                  command=save_settings).pack(pady=10)
        
    def show_temp_graph(self):
        if not self.forecast_data:
            messagebox.showwarning("Warning", "No forecast data available")
            return
            
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Temperature Trend")
        graph_window.geometry("600x400")
        
        # Create temperature graph
        fig, ax = plt.subplots(figsize=(8, 4))
        
        dates = []
        temps = []
        
        for forecast in self.forecast_data['list']:
            dates.append(datetime.fromtimestamp(forecast['dt']))
            temps.append(forecast['main']['temp'])
            
        ax.plot(dates, temps)
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Temperature Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def show_forecast_details(self):
        if not self.forecast_data:
            messagebox.showwarning("Warning", "No forecast data available")
            return
            
        details_window = tk.Toplevel(self.root)
        details_window.title("Forecast Details")
        details_window.geometry("600x400")
        
        # Create treeview for detailed forecast
        columns = ('Date', 'Time', 'Temperature', 'Description', 'Humidity', 'Wind')
        tree = ttk.Treeview(details_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        for forecast in self.forecast_data['list']:
            date_time = datetime.fromtimestamp(forecast['dt'])
            tree.insert('', 'end', values=(
                date_time.strftime("%Y-%m-%d"),
                date_time.strftime("%H:%M"),
                f"{forecast['main']['temp']}°C",
                forecast['weather'][0]['description'].capitalize(),
                f"{forecast['main']['humidity']}%",
                f"{forecast['wind']['speed']} m/s"
            ))
            
        tree.pack(fill=tk.BOTH, expand=True)
        
    def load_saved_locations(self):
        try:
            if os.path.exists('weather_locations.json'):
                with open('weather_locations.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading saved locations: {e}")
        return []
        
    def save_locations(self):
        try:
            with open('weather_locations.json', 'w') as f:
                json.dump(self.saved_locations, f)
        except Exception as e:
            print(f"Error saving locations: {e}")

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = WeatherDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main() 