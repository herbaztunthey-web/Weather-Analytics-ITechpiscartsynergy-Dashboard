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
            print(f"Error fetching {city}: {e}")

    session['weather_list'] = weather_list
    session.modified = True
    return render_template('index.html', weather_list=weather_list)


@app.route('/download_pdf')
def download_pdf():
    weather_list = session.get('weather_list', [])
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # 1. Header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.1, 0.2, 0.5)
    c.drawString(50, 750, "BABATUNDE ABASS | INTELLIGENCE REPORT")
    c.setStrokeColorRGB(0.1, 0.2, 0.5)
    c.line(50, 745, 550, 745)

    # 2. Main Data Table
    data = [["City", "Temperature (°C)", "Condition"]]
    for item in weather_list:
        data.append([item['city'], f"{item['temp']}°C", item['desc']])

    main_table = Table(data, colWidths=[150, 100, 250])
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3799")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    table_height = len(data) * 20
    main_table.wrapOn(c, 50, 400)
    main_table.drawOn(c, 50, 700 - table_height)

    # 3. Summary & Time (Bottom of PDF)
    summary_y = 100
    c.setStrokeColor(colors.black)
    c.line(50, summary_y + 40, 550, summary_y + 40)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)

    # Summary Info
    total_cities = len(weather_list)
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.drawString(50, summary_y + 20, f"TOTAL CITIES ANALYZED: {total_cities}")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, summary_y, f"Report Generated On: {gen_time}")
    c.drawRightString(550, summary_y, "System: Babatunde Abass Hub v2.0")

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Intelligence_Report.pdf")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
