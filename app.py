from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session, Response, redirect, url_for
import os
import geonamescache
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'babatunde_total_reliability_v6'

API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    error_msg = None
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        gc = geonamescache.GeonamesCache()
        continent_map = {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
            'SA': 'South America', 'OC': 'Oceania', 'AN': 'Antarctica'
        }

        for city in cities:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()
                if response.get('cod') == 200:
                    # 1. Capture the EXACT country code from THIS city response
                    actual_country_code = response['sys']['country']

                    # 2. Immediate Continent Lookup for THIS specific country
                    country_info = gc.get_countries().get(actual_country_code)
                    actual_continent = "Global"
                    if country_info:
                        c_code = country_info.get('continentcode')
                        actual_continent = continent_map.get(c_code, "Global")

                    # 3. Build the data object with locked-in values
                    weather_data = {
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'local_time': (datetime.now(timezone.utc) + timedelta(seconds=response['timezone'])).strftime("%I:%M %p"),
                        'continent': actual_continent,
                        'country_code': actual_country_code.lower()
                    }
                    weather_list.append(weather_data)

                    if response['name'] not in session['history']:
                        session['history'].insert(0, response['name'])
                        session['history'] = session['history'][:10]
                        session.modified = True
                else:
                    error_msg = f"City '{city}' not found."
            except Exception as e:
                error_msg = "Data error."

        session['last_results'] = weather_list
        return render_template('index.html', weather_list=weather_list, report_date=report_date, error_msg=error_msg, history=session['history'])

    return render_template('index.html', history=session['history'])


@app.route('/clear')
def clear_session():
    session.clear()
    return redirect(url_for('index'))


@app.route('/download')
def download_report():
    results = session.get('last_results', [])
    if not results:
        return "No data", 400
    report_content = f"BABATUNDE ABASS ANALYTICS - {datetime.now()}\n" + \
        "="*40 + "\n"
    for w in results:
        report_content += f"{w['city']} ({w['continent']}): {w['temp']}°C | {w['desc']}\n"
    return Response(report_content, mimetype="text/plain", headers={"Content-disposition": "attachment; filename=weather_report.txt"})


if __name__ == '__main__':
    app.run(debug=True)
