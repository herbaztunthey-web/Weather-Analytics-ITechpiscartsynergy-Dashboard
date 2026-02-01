import os
import io
import requests
from datetime import datetime
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

app = Flask(__name__)
# The Secret Key is what allows the 'Session' (Shopping Cart) to work safely
app.secret_key = "babatunde_abass_hub_2026"

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

    # Grab the current list from the "Cart"
    weather_list = session.get('weather_list', [])

    for city in city_names:
        params = {'q': city, 'appid': API_KEY, 'units': units}
        try:
            response = requests.get(BASE_URL, params=params).json()
            if response.get('cod') == 200:
                new_city_data = {
                    'city': response['name'],
                    'temp': response['main']['temp'],
                    'desc': response['weather'][0]['description'].capitalize(),
                    'icon': response['weather'][0]['icon'],
                    'lat': response['coord']['lat'],
                    'lon': response['coord']['lon']
                }
                if not any(item['city'] == new_city_data['city'] for item in weather_list):
                    weather_list.append(new_city_data)
        except Exception as e:
            print(f"Error: {e}")

    # SAVE THE DATA
    session['weather_list'] = weather_list

    # THIS IS THE MAGIC LINE FOR MOBILE PHONES:
    # It forces the phone browser to save the new cities.
    session.modified = True

    return render_template('index.html', weather_list=weather_list)


@app.route('/download_pdf')
def download_pdf():
    weather_list = session.get('weather_list', [])
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Profile Photo Logic
    img_path = "profile.jpg"
    if os.path.exists(img_path):
        img_x, img_y, size = 480, 710, 70
        center_x, center_y = img_x + (size/2), img_y + (size/2)
        radius = size / 2
        c.saveState()
        mask = c.beginPath()
        mask.circle(center_x, center_y, radius)
        c.clipPath(mask, stroke=0, fill=0)
        c.drawInlineImage(img_path, img_x, img_y, width=size, height=size)
        c.restoreState()
        c.setStrokeColor(colors.HexColor("#1e3799"))
        c.setLineWidth(2.5)
        c.circle(center_x, center_y, radius)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#1e3799"))
    c.drawString(50, 750, "BABATUNDE ABASS | WEATHER INTELLIGENCE REPORT")
    c.line(50, 745, 460, 745)

    # Table
    data = [["City", "Temp", "Weather Condition"]]
    for item in weather_list:
        data.append([item['city'], f"{item['temp']}°C", item['desc']])

    table = Table(data, colWidths=[130, 80, 240])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    t_height = len(data) * 20
    table.wrapOn(c, 50, 400)
    table.drawOn(c, 50, 680 - t_height)

    # Footer
    c.setStrokeColor(colors.black)
    c.line(50, 100, 550, 100)
    total = len(weather_list)
    timestamp = datetime.now().strftime("%B %d, %Y | %I:%M %p")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 80, f"TOTAL ANALYSIS: {total} CITIES")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 65, f"Report Date: {timestamp}")
    c.drawRightString(550, 65, "Babatunde Abass Intelligence Hub v2.0")

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Report.pdf")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
