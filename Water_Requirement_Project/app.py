from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import joblib
import numpy as np
import pickle

app = Flask(__name__)
app.secret_key="somethingunique"

# Load trained model and preprocessing tools
model = joblib.load("water_prediction_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load Label Encoder
with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

print(type(label_encoder))  


# Dummy user database (Replace with real DB)
users = {"admin": "password"}
print(users)
# Dummy APIs for fetching soil and weather data
SOIL_API_URL = "http://127.0.0.1:5001/get_soil_data"
WEATHER_API_URL = "http://127.0.0.1:5002/get_weather_data"

import datetime as dt

# Register custom filter
def datetimeformat(value):
    return dt.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

app.jinja_env.filters['datetimeformat'] = datetimeformat  # Register the filter


@app.route("/")
def home():
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return render_template("register.html", error="Username already exists")
        users[username] = password
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# OpenWeather API Key (Replace with your actual API key)
API_KEY = "f144a9a7f2300c65dc796cc873c53813"

# OpenWeather API Endpoint
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"  # Use "imperial" for Fahrenheit
    }

    weather_response = requests.get(WEATHER_API_URL, params=params)
    
    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        return weather_data
    else:
        return None

from datetime import datetime, timedelta  # Correct Import
import traceback # error handling

def calculate_next_irrigation(weather_data, water_required):
    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']

    k = 0.7  # Soil coefficient (can be adjusted based on soil type)

    # Approximate daily water loss calculation
    daily_water_loss = max(k * (temperature - (humidity / 100)) + (wind_speed * 0.1), 0.1)  # Prevent negative values

    if daily_water_loss == 0:  # Prevent division by zero
        return "Unknown (Insufficient Data)"

    # Calculate number of days until next irrigation
    days_until_irrigation = max(round(water_required / daily_water_loss), 1)  # Ensure at least 1 day
    print('hai')
    print(datetime.now())
    print(datetime.now() + timedelta(days=days_until_irrigation))
    # Corrected: Use datetime.now() properly
    next_irrigation_date = datetime.now() + timedelta(days=days_until_irrigation)
    print(next_irrigation_date.strftime('%Y-%m-%d'))
    # If irrigation is needed immediately
    if days_until_irrigation == 1:
        return "Irrigate Today"

    return next_irrigation_date.strftime('%Y-%m-%d')  # Return formatted date


@app.route("/process", methods=["GET", "POST"])
def process():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            crop_type = request.form.get("crop")
            lat = request.form.get("latitude")
            lon = request.form.get("longitude")

            if not crop_type or not lat or not lon:
                return render_template("dashboard.html", error="All fields are required!")

            lat, lon = float(lat), float(lon)
            print(label_encoder.classes_)
            print(crop_type)
            # Validate Crop Type
            if crop_type not in label_encoder.classes_:
                return render_template("dashboard.html", error="Invalid crop type!")

            # Fetch Soil Data
            # soil_response = requests.get(SOIL_API_URL, params={"lat": lat, "lon": lon})
            # soil_data = soil_response.json() if soil_response.status_code == 200 else None

            # # Fetch Weather Data
            # weather_response = requests.get(WEATHER_API_URL, params={"lat": lat, "lon": lon})
            # weather_data = weather_response.json() if weather_response.status_code == 200 else None
            import json 
            import soilapi2
            fetcher = soilapi2.SoilDataFetcher()
            
            soil_data = fetcher.get_all_soil_data(lat, lon)
            print(json.dumps(soil_data, indent=2))
            if soil_data==None:
                soil_data=dict()
                soil_data["soil_moisture"]=50
                soil_data["evaporation_rate"]=10
                soil_data["ph"]=10
            soil_data["ph"]=5 
            try:
                soil_data["ph"]=soil_data['ph']['0-5cm']
            except Exception as exp:
                print('error ', exp )


            # Fetch Weather Data
            weather_data = get_weather(lat, lon)

            if weather_data:
                print("Weather Data:", weather_data)
            else:
                print("Failed to fetch weather data")
                # setting defaults
                weather_data['temperature']=25
                weather_data['humidity']=50
                weather_data['rainfall']=0
                

                            
            if not soil_data or not weather_data:
                return render_template("dashboard.html", error="Failed to fetch soil/weather data!")

            # Extract values safely
            soil_moisture = soil_data.get("soil_moisture", 0)
            ph = soil_data.get("pH", 7.0)  # Default pH neutral
            evaporation_rate = soil_data.get("evaporation_rate", 0)

            temperature = weather_data.get("temperature", 25)  # Default to average temp
            humidity = weather_data.get("humidity", 50)
            rainfall = weather_data.get("rainfall", 0)
            area = float(request.form.get("area", 1.0))  # Default area = 1.0 if not provided

            # Encode Crop_Type
            crop_numeric = label_encoder.transform([crop_type])[0]

            # Prepare model input
            model_input = np.array([[crop_numeric, temperature, humidity, soil_moisture, rainfall, ph, evaporation_rate, area]])

            # Apply Scaling
            model_input_scaled = scaler.transform(model_input)

            # Predict Water Requirement
            water_required = model.predict(model_input_scaled)[0]


            next_irrigation = calculate_next_irrigation(weather_data, water_required)


            return render_template("process.html",ph=ph, soil_data=soil_data, next_irrigation=next_irrigation, crop=crop_type, water_required=round(water_required, 2), weather_data=weather_data)

        except ValueError as v:
            return render_template("dashboard.html", error=v)
        except Exception as e:
            t = traceback.format_exc()
            return render_template("dashboard.html", error=f"An error occurred: {str(e)+str(t)}")

    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)