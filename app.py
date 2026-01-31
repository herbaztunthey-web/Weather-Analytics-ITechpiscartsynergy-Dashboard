import os
import io
import requests
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "babatunde_intelligence_secret_key"  # Needed for sessions

# --- CONFIGURATION ---
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"


@app.route('/')
def home():
    # Initialize sessions if they don't exist
    if 'weather_list' not in session:
        session['weather_list'] = []
    return render_template('index.html', weather_list=session['weather_list'])


@app.route('/analyze', methods=['POST'])
def analyze():
    city = request.form.get('city')
    units = request.form.get('unit', 'metric')

    if not API_KEY:
        return "Error: API Key missing.", 500

    # 1. Fetch Current Weather
    params = {'q': city, 'appid': API_KEY, 'units': units}
    resp = requests.get(BASE_URL, params=params).json()

    if resp.get('cod') == 200:
        new_data = {
            'city': resp['name'],
            'temp': resp['main']['temp'],
            'desc': resp['weather'][0]['description'],
            'icon': resp['weather'][0]['icon'],
            'lat': resp['coord']['lat'],
            'lon': resp['coord']['lon']
        }

        # Add to session list (prevents "only one city" flaw)
        w_list = session.get('weather_list', [])
        # Keep only the last 5 searches to keep charts clean
        w_list.insert(0, new_data)
        session['weather_list'] = w_list[:5]
        session.modified = True

    return render_template('index.html', weather_list=session['weather_list'])


@app.route('/download_pdf')
def download_pdf():
    w_list = session.get('weather_list', [])
    if not w_list:
        return "No data to report. Please search for a city first.", 400

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.12, 0.22, 0.6)
    c.drawString(100, 750, "BABATUNDE ABASS | INTELLIGENCE REPORT")
    c.line(100, 740, 500, 740)

    # Data Body (Fixes the "Empty PDF" flaw)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(100, 710, "Latest Forecast Data:")

    y_position = 680
    for city in w_list:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_position, f"City: {city['city']}")
        c.setFont("Helvetica", 12)
        c.drawString(100, y_position - 20,
                     f"Condition: {city['desc']} | Temp: {city['temp']}°")
        y_position -= 50
        if y_position < 100:
            break  # Page overflow protection

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 50, "© 2026 Babatunde Abass | Verified Intelligence")
    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Abass_Intelligence.pdf")


@app.route('/maritime')
def maritime(): return render_template('maritime.html')


@app.route('/solar')
def solar(): return render_template('solar.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
