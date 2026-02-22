import os
import io
import requests
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = "babatunde_abass_hub_2026"

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
DB_PATH = "final_weather.db"


def get_ai_insight(city_name):
    """Lightweight history finder - No heavy AI Model needed, saves RAM!"""
    try:
        if not os.path.exists(DB_PATH):
            return "First time tracking this city."

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Look for the most recent previous entry for this city
        cursor.execute(
            "SELECT temp, unit, timestamp FROM history WHERE city = ? ORDER BY id DESC LIMIT 1", (city_name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return f"🤖 Intelligence Insight: Last recorded at {row[0]}{row[1]} on {row[2]}."
    except Exception as e:
        print(f"Database read error: {e}")
    return "This is a new city for your Intelligence Hub!"


@app.route('/')
def home():
    if 'weather_list' not in session:
        session['weather_list'] = []
    return render_template('index.html', weather_list=session['weather_list'])


@app.route('/analyze', methods=['POST'])
def analyze():
    session['weather_list'] = []
    raw_cities = request.form.get('city')
    units = request.form.get('unit', 'metric')

    unit_label = "°C" if units == "metric" else "°F"
    city_names = [c.strip() for c in raw_cities.split(',') if c.strip()]
    weather_list = []
    ai_insights = []

    # Ensure database table exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT, temp REAL, timestamp TEXT, unit TEXT)''')

    for city in city_names:
        params = {'q': city, 'appid': API_KEY, 'units': units}
        try:
            response = requests.get(BASE_URL, params=params).json()
            if response.get('cod') == 200:
                name = response['name']
                temp = response['main']['temp']
                desc = response['weather'][0]['description'].capitalize()

                # 1. GET PREVIOUS RECORD BEFORE SAVING NEW ONE
                insight = get_ai_insight(name)
                ai_insights.append({"city": name, "text": insight})

                # 2. SAVE CURRENT SEARCH TO SQL
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO history (city, temp, timestamp, unit) VALUES (?, ?, ?, ?)",
                               (name, temp, timestamp, unit_label))

                new_city_data = {
                    'city': name,
                    'temp': temp,
                    'desc': desc,
                    'icon': response['weather'][0]['icon'],
                    'lat': response['coord']['lat'],
                    'lon': response['coord']['lon']
                }
                weather_list.append(new_city_data)
        except Exception as e:
            print(f"Error fetching {city}: {e}")

    conn.commit()
    conn.close()

    session['weather_list'] = weather_list
    session.permanent = True
    session.modified = True

    return render_template('index.html', weather_list=weather_list, ai_insights=ai_insights)


@app.route('/download_pdf')
def download_pdf():
    weather_list = session.get('weather_list', [])
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#1e3799"))
    c.drawString(50, 750, "BABATUNDE ABASS | WEATHER INTELLIGENCE REPORT")

    # Table
    data = [["City", "Temp", "Weather Condition"]]
    for item in weather_list:
        data.append([item['city'], f"{item['temp']}°C", item['desc']])

    table = Table(data, colWidths=[130, 80, 240])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    table.wrapOn(c, 50, 400)
    table.drawOn(c, 50, 600)

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Report.pdf")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
