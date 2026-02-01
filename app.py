import os
import requests
import facebook  # Ensure you have 'facebook-sdk' in requirements.txt
from flask import Flask, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
# These pull directly from the Render Environment variables you listed
WEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_ACCESS_TOKEN')
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')


def get_weather_report(city="Lagos"):
    """Helper to fetch and format weather data."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            return f"Weather data for {city} currently unavailable."

        temp = response['main']['temp']
        desc = response['weather'][0]['description'].capitalize()
        return f"📍 {city} Intelligence Update\n🌡️ Temperature: {temp}°C\n☁️ Condition: {desc}\n#BabatundeAbassHub #Automation"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

# --- ROUTES ---


@app.route('/')
def home():
    return "Intelligence Hub is Online. Automation Ready."


@app.route('/publish')
def publish_to_fb():
    """Triggered by Cron Job to post to Facebook."""
    try:
        # 1. Generate the report
        message = get_weather_report("Lagos")

        # 2. Connect to Facebook
        graph = facebook.GraphAPI(access_token=FB_PAGE_TOKEN)

        # 3. Post to the Page Feed
        graph.put_object(parent_object=FB_PAGE_ID,
                         connection_name='feed', message=message)

        return jsonify({"status": "Success", "posted": message}), 200
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
