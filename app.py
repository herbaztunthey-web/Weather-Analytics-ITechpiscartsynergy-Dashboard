import os
import io
import requests
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "babatunde_secret_key_2026"  # This enables the 'memory'

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


@app.route('/')
def home():
    # Clear session on home visit to start a fresh report
    session['weather_list'] = []
    return render_template('index.html', weather_list=[])


@app.route('/analyze', methods=['POST'])
def analyze():
    city = request.form.get('city')
    units = request.form.get('unit', 'metric')

    params = {'q': city, 'appid': API_KEY, 'units': units}
    response = requests.get(BASE_URL, params=params).json()

    # Get the current list from memory, or start a new one
    weather_list = session.get('weather_list', [])

    if response.get('cod') == 200:
        weather_list.append({
            'city': response['name'],
            'temp': response['main']['temp'],
            'desc': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
            'lat': response['coord']['lat'],
            'lon': response['coord']['lon']
        })
        # Save the updated list back to memory
        session['weather_list'] = weather_list
        session.modified = True

    return render_template('index.html', weather_list=weather_list)


@app.route('/download_pdf')
def download_pdf():
    weather_list = session.get('weather_list', [])

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Branding Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.12, 0.22, 0.6)
    c.drawString(100, 750, "BABATUNDE ABASS | INTELLIGENCE REPORT")
    c.setStrokeColorRGB(0, 0.82, 1.0)
    c.line(100, 740, 500, 740)

    # DATA SECTION - This fixes the empty PDF!
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    y_pos = 710

    if not weather_list:
        c.drawString(
            100, y_pos, "No data available. Please run an analysis first.")
    else:
        for item in weather_list:
            c.drawString(100, y_pos, f"City: {item['city']}")
            c.setFont("Helvetica", 11)
            c.drawString(
                100, y_pos - 15, f"Temperature: {item['temp']}°C | Condition: {item['desc']}")
            y_pos -= 45  # Move down for the next city
            c.setFont("Helvetica-Bold", 12)

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 50, "© 2026 Babatunde Abass | Intelligence Hub Verified")

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Abass_Report.pdf")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
