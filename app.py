import os
import io
import requests
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "babatunde_abass_hub_2026"

# This pulls from your Render Dashboard
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


@app.route('/')
def home():
    session['weather_list'] = []
    return render_template('index.html', weather_list=[])


@app.route('/analyze', methods=['POST'])
def analyze():
    raw_cities = request.form.get('city')
    units = request.form.get('unit', 'metric')
    city_names = [c.strip() for c in raw_cities.split(',') if c.strip()]
    weather_list = session.get('weather_list', [])

    for city in city_names:
        params = {'q': city, 'appid': API_KEY, 'units': units}
        try:
            response = requests.get(BASE_URL, params=params).json()
            if response.get('cod') == 200:
                new_city_data = {
                    'city': response['name'],
                    'temp': response['main']['temp'],
                    'desc': response['weather'][0]['description'],
                    'icon': response['weather'][0]['icon'],
                    'lat': response['coord']['lat'],
                    'lon': response['coord']['lon']
                }
                if not any(item['city'] == new_city_data['city'] for item in weather_list):
                    weather_list.append(new_city_data)
        except Exception as e:
            print(f"Error fetching {city}: {e}")

    session['weather_list'] = weather_list
    session.modified = True
    return render_template('index.html', weather_list=weather_list)


@app.route('/download_pdf')
def download_pdf():
    weather_list = session.get('weather_list', [])
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.12, 0.22, 0.6)
    c.drawString(100, 750, "BABATUNDE ABASS | WEATHER INTELLIGENCE REPORT")
    c.line(100, 740, 500, 740)
    y_pos = 700
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    for item in weather_list:
        c.drawString(100, y_pos, f"City: {item['city']}")
        c.setFont("Helvetica", 11)
        c.drawString(100, y_pos - 15,
                     f"Temp: {item['temp']}°C | Condition: {item['desc']}")
        y_pos -= 45
        if y_pos < 100:
            c.showPage()
            y_pos = 750
            c.setFont("Helvetica-Bold", 12)
    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Abass_Report.pdf")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
