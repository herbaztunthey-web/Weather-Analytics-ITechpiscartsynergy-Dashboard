from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session
import os
import geonamescache
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'babatunde_secret_key'  # Needed for Search History session

API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    error_msg = None
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    # Initialize search history in session if not exists
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        gc = geonamescache.GeonamesCache()
        continent_map = {'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe',
                         'NA': 'North America', 'SA': 'South America', 'OC': 'Oceania', 'AN': 'Antarctica'}

        for city in cities:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()
                if response.get('cod') == 200:
                    # 1. Calculate Local Time
                    offset = response['timezone']
                    local_dt = datetime.now(
                        timezone.utc) + timedelta(seconds=offset)

                    # 2. Continent & Country Logic
                    country_code = response['sys']['country']
                    country_info = gc.get_countries().get(country_code)
                    continent_name = continent_map.get(country_info.get(
                        'continentcode'), "Unknown") if country_info else "Unknown"

                    # 3. Dynamic Background Mapping
                    main_weather = response['weather'][0]['main'].lower()

                    weather_data = {
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'local_time': local_dt.strftime("%I:%M %p"),
                        'continent': continent_name,
                        'country_code': country_code,
                        'main_weather': main_weather
                    }
                    weather_list.append(weather_data)

                    # Update Search History (Keep last 5)
                    if response['name'] not in session['history']:
                        session['history'].insert(0, response['name'])
                        session['history'] = session['history'][:5]
                        session.modified = True
                else:
                    error_msg = f"City '{city}' not found. Please check spelling."
            except Exception as e:
                error_msg = "Connection error. Please try again later."

        return render_template('index.html', weather_list=weather_list, report_date=report_date, error_msg=error_msg, history=session['history'])

    return render_template('index.html', history=session['history'])


if __name__ == '__main__':
    app.run(debug=True)
