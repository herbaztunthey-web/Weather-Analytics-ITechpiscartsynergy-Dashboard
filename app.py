import os
import requests
import facebook  # The SDK we added to requirements.txt
from flask import Flask, jsonify

app = Flask(__name__)


def fetch_weather():
    """Fetches weather for your primary hub location."""
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    # Let's use a default city; you can change this to your location
    city = "Lagos"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"🌍 {city} Intelligence Briefing\n🌡️ Temp: {temp}°C\n☁️ Status: {desc.title()}\n#BabatundeAbassHub #Automation"
    return None


@app.route('/auto-post')
def auto_post():
    """The trigger route that sends the post to Facebook."""
    try:
        # Pulling keys from your Render environment
        page_id = os.environ.get('FB_PAGE_ID')
        token = os.environ.get('FB_PAGE_ACCESS_TOKEN')

        # 1. Get the content
        message = fetch_weather()
        if not message:
            return "Failed to fetch weather data", 500

        # 2. Connect to Facebook and Post
        graph = facebook.GraphAPI(access_token=token)
        graph.put_object(parent_object=page_id,
                         connection_name='feed', message=message)

        return jsonify({"status": "Success", "message": "Facebook post published!"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500


@app.route('/')
def home():
    return "Intelligence Hub is Online & Monitoring."


if __name__ == "__main__":
    app.run()
