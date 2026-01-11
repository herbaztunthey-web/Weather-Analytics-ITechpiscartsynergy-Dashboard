from datetime import datetime
import requests
from flask import Flask, render_template, request, session, redirect, url_for, Response, flash
import os
import sqlite3
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'babatunde_map_intelligence_2026'

API_KEY = os.getenv('WEATHER_API_KEY')
DB_PATH = os.path.join(os.getcwd(), 'final_weather.db')

# --- DATABASE AUTO-FIX FOR RENDER ---


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS history 
                        (city TEXT, temp REAL, unit TEXT, timestamp TEXT)''')
        try:
            conn.execute('ALTER TABLE history ADD COLUMN unit TEXT')
        except sqlite3.OperationalError:
            pass
        conn.commit()
    finally:
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
        'SELECT city, temp, unit, timestamp FROM history ORDER BY timestamp DESC LIMIT 10').fetchall()
    conn.close()

    return render_template('index.html', weather_list=weather_list, forecast_data=forecast_data,
                           report_date=report_date, history=history, unit=unit, api_key_from_env=API_KEY)


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

                # Alert detection logic
                desc = r_curr['weather'][0]['description'].lower()
                has_alert = any(word in desc for word in [
                                'storm', 'hurricane', 'tornado', 'heavy', 'danger'])
                alert_msg = f"SEVERE WEATHER: {desc.upper()}" if has_alert else None

                data = {'city': r_curr['name'], 'temp': round(r_curr['main']['temp'], 1),
                        'desc': r_curr['weather'][0]['description'], 'icon': r_curr['weather'][0]['icon'],
                        'lat': lat, 'lon': lon, 'alert': alert_msg}
                weather_list.append(data)

                # Log to DB for historical reference
                conn = sqlite3.connect(DB_PATH)
                conn.execute('INSERT INTO history (city, temp, unit, timestamp) VALUES (?, ?, ?, ?)',
                             (data['city'], data['temp'], unit, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                conn.close()

                r_fore = requests.get(fore_url).json()
                if r_fore.get('cod') == "200":
                    daily = [item for item in r_fore['list']
                             if "12:00:00" in item['dt_txt']]
                    forecast_map[r_curr['name']] = [
                        {'temp': round(f['main']['temp'], 1), 'date': f['dt_txt'][5:10]} for f in daily]
        except:
            flash("Connection Error")

    session['last_results'] = weather_list
    session['forecast_data'] = forecast_map
    return redirect(url_for('index'))


@app.route('/download_pdf')
def download_pdf():
    # PULL ONLY CURRENT RESULTS FROM SESSION
    weather_list = session.get('last_results', [])
    unit = session.get('unit', 'metric')

    if not weather_list:
        return redirect(url_for('index'))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFillColor(colors.HexColor("#1e3799"))
    p.rect(0, height - 80, width, 80, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 45,
                 " WEATHER FORECAST AND DATA ANALYSIS INTELLIGENCE REPORT")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 60,
                 f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Table Headers
    y = height - 120
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "LOCATION")
    p.drawString(250, y, "TEMPERATURE")
    p.drawString(400, y, "CONDITION")
    p.line(50, y - 5, 550, y - 5)

    # Table Rows
    y -= 25
    p.setFont("Helvetica", 11)
    symbol = "°C" if unit == 'metric' else "°F"

    for w in weather_list:
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(50, y, str(w['city']))
        p.drawString(250, y, f"{w['temp']}{symbol}")
        p.drawString(400, y, str(w['desc']).capitalize())
        p.setStrokeColor(colors.lightgrey)
        p.line(50, y - 5, 550, y - 5)
        y -= 25

    p.showPage()
    p.save()
    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf', headers={"Content-Disposition": "attachment; filename=Intelligence_Report.pdf"})


if __name__ == '__main__':
    app.run(debug=True)
