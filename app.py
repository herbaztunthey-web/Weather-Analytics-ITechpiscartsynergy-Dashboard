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

# Get API Key from Render Environment Variables
API_KEY = os.getenv('WEATHER_API_KEY')

# Database path fix for Render (ensures it writes to a valid directory)
DB_PATH = os.path.join(os.getcwd(), 'final_weather.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS history (city TEXT, temp REAL, timestamp DATETIME)')
    conn.close()

def save_search(city, temp):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO history (city, temp, timestamp) VALUES (?, ?, ?)',
                 (city, temp, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    # Keep the weather results in the session so they don't disappear on refresh
    weather_list = session.get('last_results', [])
    stats = session.get('last_stats', {})
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    conn = sqlite3.connect(DB_PATH)
    history = conn.execute(
        'SELECT city, temp FROM history ORDER BY timestamp DESC LIMIT 5').fetchall()
    conn.close()
    
    return render_template('index.html', 
                           weather_list=weather_list, 
                           report_date=report_date, 
                           stats=stats, 
                           history=history, 
                           api_key_from_env=API_KEY)

@app.route('/analyze', methods=['POST'])
def analyze():
    city_input = request.form.get('city', '')
    cities = [c.strip() for c in city_input.split(',') if c.strip()]
    weather_list = []

    if not API_KEY:
        flash("System Error: API Key missing in Render Environment Settings.")
        return redirect(url_for('index'))

    for city in cities:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
        try:
            r = requests.get(url).json()
            if r.get('cod') == 200:
                utc_now = datetime.now(timezone.utc)
                local_dt = utc_now + timedelta(seconds=int(r.get('timezone', 0)))
                data = {
                    'city': r['name'], 'temp': round(r['main']['temp'], 1),
                    'humidity': r['main']['humidity'], 'desc': r['weather'][0]['description'],
                    'icon': r['weather'][0]['icon'], 'lat': r['coord']['lat'],
                    'lon': r['coord']['lon'], 'local_time': local_dt.strftime("%I:%M %p")
                }
                weather_list.append(data)
                save_search(r['name'], data['temp'])
            else:
                flash(f"Error for {city}: {r.get('message', 'City not found')}")
        except Exception as e:
            flash(f"Connection failed for {city}")

    if weather_list:
        session['last_results'] = weather_list
        session['last_stats'] = {
            'hottest': max(weather_list, key=lambda x: x['temp'])['city'],
            'coldest': min(weather_list, key=lambda x: x['temp'])['city'],
            'avg_temp': round(sum(d['temp'] for d in weather_list) / len(weather_list), 1)
        }
    
    return redirect(url_for('index'))

@app.route('/download_pdf')
def download_pdf():
    weather_list = session.get('last_results', [])
    if not weather_list:
        return redirect(url_for('index'))
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height - 50, "GEOSPATIAL WEATHER INTELLIGENCE REPORT")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, height - 70, f"Analyst: Babatunde Abass | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    p.line(50, height - 80, width - 50, height - 80)
    y = height - 120
    for w in weather_list:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(70, y, f"Location: {w['city']}")
        p.setFont("Helvetica", 11)
        p.drawString(70, y - 18, f"Temp: {w['temp']}°C | Time: {w['local_time']} | Coord: {w['lat']}, {w['lon']}")
        y -= 60
    p.showPage()
    p.save()
    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf', headers={"Content-Disposition": "attachment; filename=Report.pdf"})

@app.route('/export')
def export_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('SELECT * FROM history')
    results = cursor.fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['City', 'Temperature', 'Timestamp'])
    cw.writerows(results)
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=history.csv"})

@app.route('/clear')
def clear_session():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)