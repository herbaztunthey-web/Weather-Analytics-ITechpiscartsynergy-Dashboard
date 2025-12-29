from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session
import os
import geonamescache
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# CRITICAL: Secret key is required to save your "Recent Searches"
app.secret_key = 'babatunde_analytics_key_2025'

API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    error_msg = None
    # Professional timestamp for the header
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    # Initialize search history in the browser session if it doesn't exist
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        # Clean the input and split by commas for multi-city search
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        gc = geonamescache.GeonamesCache()
        continent_map = {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
            'SA': 'South America', 'OC': 'Oceania', 'AN': 'Antarctica'
        }

        for city in cities:
            # Using HTTPS for security and professional deployment
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()

                # Check if the city exists (Error Handling)
                if response.get('cod') == 200:
                    # 1. Precise Local Time Calculation
                    offset = response['timezone']
                    local_dt = datetime.now(
                        timezone.utc) + timedelta(seconds=offset)

                    # 2. Continent Mapping Logic
                    country_code = response['sys']['country']
                    country_info = gc.get_countries().get(country_code)
                    continent_name = continent_map.get(country_info.get(
                        'continentcode'), "Global") if country_info else "Global"

                    # 3. Compile all data for the Flag Cards
                    weather_data = {
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'local_time': local_dt.strftime("%I:%M %p"),
                        'continent': continent_name,
                        'country_code': country_code  # Used for flag backgrounds
                    }
                    weather_list.append(weather_data)

                    # 4. Update Search History (Keep top 5 unique searches)
                    if response['name'] not in session['history']:
                        session['history'].insert(0, response['name'])
                        session['history'] = session['history'][:5]
                        session.modified = True
                else:
                    # Professional Error Message
                    error_msg = f"Analysis Failed: City '{city}' not recognized. Please verify spelling."

            except Exception as e:
                error_msg = "System Error: Unable to reach weather servers. Please try again."

        return render_template('index.html', weather_list=weather_list, report_date=report_date, error_msg=error_msg, history=session['history'])

    # Initial page load shows the history
    return render_template('index.html', history=session['history'])


if __name__ == '__main__':
    app.run(debug=True)
