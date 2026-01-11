from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session, redirect, url_for, Response, flash
import os
import sqlite3
import io
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'babatunde_map_intelligence_2026'

API_KEY = os.getenv('WEATHER_API_KEY')
DB_PATH = os.path.join(os.getcwd(), 'final_weather.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS history (city TEXT, temp REAL, unit TEXT, timestamp DATETIME)')
    conn.close()


def save_search(city, temp, unit):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO history (city, temp, unit, timestamp) VALUES (?, ?, ?, ?)',
                 (city, temp, unit, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    weather_list = session.get('last_results', [])
    forecast_data = session.get('forecast_data', {})
    unit = session.get('unit', 'metric')
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    conn = sqlite3.connect(DB_PATH)
    history = conn.execute(
        'SELECT city, temp, unit FROM history ORDER BY timestamp DESC LIMIT 5').fetchall()
    conn.close()

    return render_template('index.html',
                           weather_list=weather_list,
                           forecast_data=forecast_data,
                           report_date=report_date,
                           history=history,
                           unit=unit,
                           api_key_from_env=API_KEY)


@app.route('/analyze', methods=['POST'])
def analyze():
    city_input = request.form.get('city', '')
    unit = request.form.get('unit', 'metric')
    session['unit'] = unit
    cities = [c.strip() for c in city_input.split(',') if c.strip()]

    weather_list = []
    forecast_map = {}

    for city in cities:
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units={unit}&appid={API_KEY}"
        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units={unit}&appid={API_KEY}"

        try:
            r_curr = requests.get(curr_url).json()
            if r_curr.get('cod') == 200:
                lat, lon = r_curr['coord']['lat'], r_curr['coord']['lon']

                # NEW: Fetch Air Quality Data
                aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
                aqi_res = requests.get(aqi_url).json()
                aqi_val = aqi_res['list'][0]['main']['aqi'] if 'list' in aqi_res else "N/A"

                data = {
                    'city': r_curr['name'], 'temp': round(r_curr['main']['temp'], 1),
                    'desc': r_curr['weather'][0]['description'], 'icon': r_curr['weather'][0]['icon'],
                    'lat': lat, 'lon': lon, 'aqi': aqi_val
                }
                weather_list.append(data)
                save_search(r_curr['name'], data['temp'], unit)

                # Fetch Forecast
                r_fore = requests.get(fore_url).json()
                if r_fore.get('cod') == "200":
                    daily = [item for item in r_fore['list']
                             if "12:00:00" in item['dt_txt']]
                    forecast_map[r_curr['name']] = [
                        {'temp': round(f['main']['temp'], 1), 'date': f['dt_txt'][:10]} for f in daily]
            else:
                flash(f"Error: {r_curr.get('message', 'Not found')}")
        except:
            flash("API Connection Failed")

    session['last_results'] = weather_list
    session['forecast_data'] = forecast_map
    return redirect(url_for('index'))


@app.route('/clear')
def clear_session():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
