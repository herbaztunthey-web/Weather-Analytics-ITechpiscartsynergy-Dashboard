from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request
import os
import geonamescache
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- YOUR CONFIGURATION ---
API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    # Current time for the general report header
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        gc = geonamescache.GeonamesCache()
        continent_map = {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe',
            'NA': 'North America', 'SA': 'South America',
            'OC': 'Oceania', 'AN': 'Antarctica'
        }

        for city in cities:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()
                if response.get('cod') == 200:
                    # --- NEW CALCULATION LOGIC ---
                    # 1. Calculate specific Local Time for that city
                    offset = response['timezone']
                    local_dt = datetime.now(
                        timezone.utc) + timedelta(seconds=offset)
                    city_local_time = local_dt.strftime("%I:%M %p")

                    # 2. Get Continent Name
                    country_code = response['sys']['country']
                    country_info = gc.get_countries().get(country_code)
                    continent_code = country_info.get(
                        'continentcode') if country_info else "Unknown"
                    continent_name = continent_map.get(
                        continent_code, "Unknown Region")

                    weather_list.append({
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'local_time': city_local_time,  # Added
                        'continent': continent_name    # Added
                    })
            except Exception as e:
                print(f"Error fetching {city}: {e}")

        return render_template('index.html', weather_list=weather_list, report_date=report_date)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
