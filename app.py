import os
import requests
import facebook
from flask import Flask, jsonify, redirect, url_for

app = Flask(__name__)

# CONFIGURATION
WEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_ACCESS_TOKEN')
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')


def get_weather_report(cities="Lagos"):
    """Fetches weather and returns a string for display/posting."""
    cities_list = cities.split(",") if isinstance(cities, str) else [cities]
    reports = []
    for city in cities_list:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city.strip()}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") == 200:
            temp = response['main']['temp']
        desc = response['weather'][0]['description'].capitalize()
        return f"📍 {city} Briefing: {temp}°C, {desc}."
    return "Weather service temporarily unavailable."


@app.route('/')
def home():
    # This now shows the ACTUAL weather on your screen!
    report = get_weather_report("Lagos")
    return f"<h1>Intelligence Hub Live</h1><p>{report}</p><hr><p>Status: Online & Monitoring</p>"


@app.route('/publish')
def publish_to_fb():
    try:
        message = get_weather_report("Lagos")
        graph = facebook.GraphAPI(access_token=FB_PAGE_TOKEN)
        graph.put_object(parent_object=FB_PAGE_ID,
                         connection_name='feed', message=message)
        return jsonify({"status": "Success", "posted": message})
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500


if __name__ == "__main__":
    app.run()
