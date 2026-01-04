from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, Response
import os
import sqlite3
import io
import csv
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'babatunde_map_intelligence_2025'

API_KEY = os.getenv('WEATHER_API_KEY')

# --- DATABASE SETUP ---


def init_db():
    conn = sqlite3.connect('final_weather.db')
    conn.execute(
        'CREATE TABLE IF NOT EXISTS history (city TEXT, temp REAL, timestamp DATETIME)')
    conn.close()


def save_search(city, temp):
    conn = sqlite3.connect('final_weather.db')
    conn.execute('INSERT INTO history (city, temp, timestamp) VALUES (?, ?, ?)',
                 (city, temp, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect('final_weather.db')
    cursor = conn.execute(
        'SELECT city, temp FROM history ORDER BY timestamp DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    return rows


init_db()


@app.route('/export')
def export_data():
    conn = sqlite3.connect('final_weather.db')
    cursor = conn.execute('SELECT * FROM history')
    results = cursor.fetchall()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['City', 'Temperature', 'Timestamp'])
    cw.writerows(results)

    return Response(si.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=weather_history.csv"})


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    stats = {}
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        for city in cities:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()
                if response.get('cod') == 200:
                    temp = round(response['main']['temp'], 1)
                    weather_data = {
                        'city': response['name'],
                        'temp': temp,
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'lat': response['coord']['lat'],
                        'lon': response['coord']['lon'],
                        'local_time': (datetime.now(timezone.utc) + timedelta(seconds=response['timezone'])).strftime("%I:%M %p")
                    }
                    weather_list.append(weather_data)
                    save_search(response['name'], temp)
            except:
                pass

        if weather_list:
            stats['hottest'] = max(
                weather_list, key=lambda x: x['temp'])['city']
            stats['coldest'] = min(
                weather_list, key=lambda x: x['temp'])['city']
            stats['avg_temp'] = round(
                sum(d['temp'] for d in weather_list) / len(weather_list), 1)

    recent_history = get_history()
    return render_template('index.html', weather_list=weather_list, report_date=report_date, stats=stats, history=recent_history)


@app.route('/clear')
def clear_session():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
