from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = "e3b8cf522cd44439b46153354250311"
BASE_URL = "http://api.weatherapi.com/v1"

def call_api(endpoint, params):
    url = f"{BASE_URL}/{endpoint}.json"
    params["key"] = API_KEY
    response = requests.get(url, params=params)
    return response.json()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_weather", methods=["POST"])
def get_weather():
    location = request.form.get("location")
    date_input = request.form.get("date", "").strip()
    today = datetime.now().strftime("%Y-%m-%d")

    if not location:
        return jsonify({"error": "Please enter a location"})

    try:
        if not date_input or date_input == today:
            weather_data = call_api("current", {"q": location, "aqi": "yes"})
            data_type = "Current Weather"
        elif date_input < today:
            weather_data = call_api("history", {"q": location, "dt": date_input})
            data_type = f"Weather on {date_input}"
        else:
            weather_data = call_api("future", {"q": location, "dt": date_input})
            data_type = f"Forecast for {date_input}"

        alerts_data = call_api("alerts", {"q": location})

        return jsonify({
            "type": data_type,
            "weather": weather_data,
            "alerts": alerts_data
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
