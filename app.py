import os
import io
import requests
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
# This secret key is what allows the session to 'remember' multiple cities
app.secret_key = "babatunde_abass_hub_2026"

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


@app.route('/')
def home():
    # Initializes an empty list when you first load the page
    session['weather_list'] = []
    return render_template('index.html', weather_list=[])


@app.route('/analyze', methods=['POST'])
def analyze():
    city = request.form.get('city')
    units = request.form.get('unit', 'metric')

    params = {'q': city, 'appid': API_KEY, 'units': units}
    response = requests.get(BASE_URL, params=params).json()

    # FIX: Retrieve the current list from memory instead of creating a new one
    weather_list = session.get('weather_list', [])

    if response.get('cod') == 200:
        new_city_data = {
            'city': response['name'],
            'temp': response['main']['temp'],
            'desc': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
            'lat': response['coord']['lat'],
            'lon': response['coord']['lon']
        }

        # APPEND: This adds the new city to the existing list
        weather_list.append(new_city_data)

        # SAVE: Store the updated list back into the session memory
        session['weather_list'] = weather_list
        session.modified = True

    return render_template('index.html', weather_list=weather_list)


@app.route('/download_pdf')
def download_pdf():
    # Pulls all cities stored in the session for the report
    weather_list = session.get('weather_list', [])

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Branded Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.12, 0.22, 0.6)
    c.drawString(100, 750, "BABATUNDE ABASS |WEATHER INTELLIGENCE REPORT")
    c.line(100, 740, 500, 740)

    # DATA SECTION: Loops through the list to print every city
    y_pos = 700
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)

    for item in weather_list:
        c.drawString(100, y_pos, f"City: {item['city']}")
        c.setFont("Helvetica", 11)
        c.drawString(100, y_pos - 15,
                     f"Temp: {item['temp']}°C | Condition: {item['desc']}")
        y_pos -= 45  # Moves the pen down for the next city
        c.setFont("Helvetica-Bold", 12)
        if y_pos < 100:  # Simple page break check
            c.showPage()
            y_pos = 750

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Abass_Report.pdf")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
