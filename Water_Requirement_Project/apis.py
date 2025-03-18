from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# API KEYS (Replace with your actual keys)
OPENWEATHER_API_KEY = "f144a9a7f2300c65dc796cc873c53813"  # Get from https://home.openweathermap.org/api_keys
NASA_SOIL_API_URL = "https://api.nasa.gov/soil_data"  #
NASA_API_KEY = "xN9WaeMgixyxjcWtuyAz1EQHNTaXpY48UOW0cm8P"  # Get from https://api.nasa.gov/

### 1️⃣ Fetch Weather Data (Temperature, Humidity, Rainfall) ###
@app.route("/get_weather", methods=["GET"])
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(weather_url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch weather data", "details": data}), 500

        weather_info = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0),  # Rainfall in last 1 hour (if available)
        }
        return jsonify(weather_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


### 2️⃣ Fetch Soil Data (Soil Moisture, pH, Evaporation Rate) ###
@app.route("/get_soil", methods=["GET"])
def get_soil():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    soil_url = f"{NASA_SOIL_API_URL}?lat={lat}&lon={lon}&api_key={NASA_API_KEY}"
    print(soil_url)
    try:
        response = requests.get(soil_url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch soil data", "details": data}), 500

        soil_info = {
            "soil_moisture": data["soil_moisture"],
            "pH": data["soil_ph"],
            "evaporation_rate": data["evaporation_rate"],
        }
        return jsonify(soil_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
