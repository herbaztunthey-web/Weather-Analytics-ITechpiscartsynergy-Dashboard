import os
import io
import requests
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# --- CONFIGURATION ---
# This now matches the "Variable Name" box on Render
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# --- 1. THE HUB ---


@app.route('/')
def home():
    return render_template('index.html')

# --- 2. THE WEATHER MODULE ---


@app.route('/analyze', methods=['POST'])
def analyze():
    city = request.form.get('city')
    units = request.form.get('unit', 'metric')

    # Security check: If the API Key is missing from Render, show an error
    if not API_KEY:
        return "Error: OPENWEATHER_API_KEY not found in Render Environment Variables.", 500

    params = {'q': city, 'appid': API_KEY, 'units': units}
    response = requests.get(BASE_URL, params=params).json()

    weather_list = []
    if response.get('cod') == 200:
        weather_list.append({
            'city': response['name'],
            'temp': response['main']['temp'],
            'desc': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
            'lat': response['coord']['lat'],
            'lon': response['coord']['lon'],
            'alert': "High Heat" if response['main']['temp'] > 35 else None
        })

    return render_template('weather.html', weather_list=weather_list)

# --- 3. THE BRANDED PDF ENGINE ---


@app.route('/download_pdf')
def download_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.12, 0.22, 0.6)
    c.drawString(100, 750, "BABATUNDE ABASS | INTELLIGENCE REPORT")

    c.setStrokeColorRGB(0, 0.82, 1.0)
    c.line(100, 740, 500, 740)

    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(100, 710, "Report Status: Official Data Forecast")
    c.drawString(
        100, 690, "Generated via: The Babatunde Abass Intelligence Hub")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(
        100, 50, "© 2026 Babatunde Abass | Data Analytics & Global Forecasting")
    c.drawString(400, 50, "Verified on Render Cloud")

    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Abass_Report.pdf")

# --- 4. SPECIALIZED MODULES ---


@app.route('/maritime')
def maritime():
    return render_template('maritime.html')


@app.route('/solar')
def solar():
    return render_template('solar.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render uses 10000 by default
    app.run(host='0.0.0.0', port=port)
