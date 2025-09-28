import tkinter as tk
from tkinter import ttk, messagebox
import threading
from weather_api import get_current_weather, get_forecast, get_weather_icon

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("800x600")
        
        # Variables
        self.city_var = tk.StringVar()
        self.units_var = tk.StringVar(value="metric")
        self.current_weather = {}
        self.forecast_data = {}
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Location", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="City:").grid(row=0, column=0, sticky=tk.W)
        city_entry = ttk.Entry(input_frame, textvariable=self.city_var, width=30)
        city_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(input_frame, text="Get Weather", command=self.fetch_weather).grid(row=0, column=2, padx=(10, 0))
        
        # Units
        ttk.Label(input_frame, text="Units:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Radiobutton(input_frame, text="Celsius", variable=self.units_var, value="metric").grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Radiobutton(input_frame, text="Fahrenheit", variable=self.units_var, value="imperial").grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        
        # Current weather frame
        current_frame = ttk.LabelFrame(main_frame, text="Current Weather", padding="10")
        current_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.current_label = ttk.Label(current_frame, text="Enter a city and click 'Get Weather'")
        self.current_label.grid(row=0, column=0, sticky=tk.W)
        
        # Forecast frame
        forecast_frame = ttk.LabelFrame(main_frame, text="Forecast", padding="10")
        forecast_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Hourly forecast
        hourly_frame = ttk.LabelFrame(forecast_frame, text="Hourly (Next 24 hours)", padding="5")
        hourly_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.hourly_canvas = tk.Canvas(hourly_frame, height=100)
        self.hourly_scrollbar = ttk.Scrollbar(hourly_frame, orient="horizontal", command=self.hourly_canvas.xview)
        self.hourly_canvas.configure(xscrollcommand=self.hourly_scrollbar.set)
        
        self.hourly_frame = ttk.Frame(self.hourly_canvas)
        self.hourly_canvas.create_window((0, 0), window=self.hourly_frame, anchor="nw")
        self.hourly_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.hourly_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Daily forecast
        daily_frame = ttk.LabelFrame(forecast_frame, text="Daily (Next 5 days)", padding="5")
        daily_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.daily_frame = ttk.Frame(daily_frame)
        self.daily_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(1, weight=1)
        current_frame.columnconfigure(0, weight=1)
        forecast_frame.columnconfigure(0, weight=1)
        hourly_frame.columnconfigure(0, weight=1)
        daily_frame.columnconfigure(0, weight=1)
        
    def fetch_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return
        
        units = self.units_var.get()
        
        # Run in thread to avoid blocking GUI
        threading.Thread(target=self._fetch_weather_thread, args=(city, units), daemon=True).start()
        
    def _fetch_weather_thread(self, city, units):
        try:
            # Fetch current weather
            self.current_weather = get_current_weather(city, units)
            
            # Fetch forecast
            self.forecast_data = get_forecast(city, units)
            
            # Update GUI in main thread
            self.root.after(0, self.update_weather_display)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def update_weather_display(self):
        # Update current weather
        unit_symbol = "°C" if self.units_var.get() == "metric" else "°F"
        wind_unit = "m/s" if self.units_var.get() == "metric" else "mph"
        
        current_text = f"{self.current_weather['city']}, {self.current_weather['country']}\n" \
                      f"Temperature: {self.current_weather['temperature']}{unit_symbol}\n" \
                      f"Description: {self.current_weather['description'].capitalize()}\n" \
                      f"Humidity: {self.current_weather['humidity']}%\n" \
                      f"Wind Speed: {self.current_weather['wind_speed']} {wind_unit}\n" \
                      f"Pressure: {self.current_weather['pressure']} hPa"
        
        self.current_label.config(text=current_text)
        
        # Update hourly forecast
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()
        
        for i, hour in enumerate(self.forecast_data["hourly"][:8]):  # Next 24 hours (8 entries)
            frame = ttk.Frame(self.hourly_frame)
            frame.grid(row=0, column=i, padx=5, pady=5)
            
            time = hour["time"][11:16]  # HH:MM
            ttk.Label(frame, text=time).grid(row=0, column=0)
            
            try:
                icon = get_weather_icon(hour["icon"], (32, 32))
                icon_label = ttk.Label(frame, image=icon)
                icon_label.image = icon
                icon_label.grid(row=1, column=0)
            except:
                ttk.Label(frame, text="Icon").grid(row=1, column=0)
            
            ttk.Label(frame, text=f"{hour['temperature']}{unit_symbol}").grid(row=2, column=0)
            ttk.Label(frame, text=hour["description"].capitalize()).grid(row=3, column=0)
        
        self.hourly_frame.update_idletasks()
        self.hourly_canvas.configure(scrollregion=self.hourly_canvas.bbox("all"))
        
        # Update daily forecast
        for widget in self.daily_frame.winfo_children():
            widget.destroy()
        
        for i, day in enumerate(self.forecast_data["daily"][:5]):
            frame = ttk.Frame(self.daily_frame)
            frame.grid(row=0, column=i, padx=10, pady=5)
            
            day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]  # Simple day names
            ttk.Label(frame, text=day_name).grid(row=0, column=0)
            
            try:
                icon = get_weather_icon(day["icon"], (48, 48))
                icon_label = ttk.Label(frame, image=icon)
                icon_label.image = icon
                icon_label.grid(row=1, column=0)
            except:
                ttk.Label(frame, text="Icon").grid(row=1, column=0)
            
            ttk.Label(frame, text=f"{day['min_temp']}{unit_symbol} / {day['max_temp']}{unit_symbol}").grid(row=2, column=0)
            ttk.Label(frame, text=day["description"].capitalize()).grid(row=3, column=0)
