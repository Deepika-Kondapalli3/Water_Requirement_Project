from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/get_weather_data", methods=["GET"])
def get_weather_data():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    # Dummy weather data (Replace with real API in production)
    weather_data = {
        "latitude": lat,
        "longitude": lon,
        "temperature": 30.5,  # °C
        "humidity": 70,  # %
        "rainfall": 15.0,  # mm
    }

    return jsonify(weather_data)

if __name__ == "__main__":
    app.run(port=5002, debug=True)
