import os
import io
import requests
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "babatunde_abass_hub_2026"

# Ensure this matches your Render Environment Variable name exactly
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


@app.route('/')
def home():
    session['weather_list'] = []
    return render_template('index.html', weather_list=[])


@app.route('/analyze', methods=['POST'])
def analyze():
    raw_cities = request.form.get('city')
    city_names = [c.strip() for c in raw_cities.split(',') if c.strip()]
    weather_list = session.get('weather_list', [])

    for city in city_names:
        params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
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
            print(f"Error: {e}")

    session['weather_list'] = weather_list
    session.modified = True
    return render_template('index.html', weather_list=weather_list)


@app.route('/download_pdf')
def download_pdf():
    weather_list = session.get('weather_list', [])
    buffer = io.BytesIO()

    # Use SimpleDocTemplate for professional layout
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # 1. Professional Title
    title = Paragraph(
        "BABATUNDE ABASS | WEATHER INTELLIGENCE REPORT", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # 2. Structured Table Data
    data = [["CITY NAME", "TEMPERATURE", "WEATHER CONDITION"]]
    total_temp = 0
    for item in weather_list:
        data.append([item['city'], f"{item['temp']}°C", item['desc'].title()])
        total_temp += item['temp']

    # 3. Apply the "Prop" Table Styling
    report_table = Table(data, colWidths=[180, 100, 200])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0),
         colors.HexColor("#1e3799")),  # Royal Blue Header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
    ])
    report_table.setStyle(style)
    elements.append(report_table)

    # 4. Data Summary Section
    if weather_list:
        elements.append(Spacer(1, 30))
        avg_temp = round(total_temp / len(weather_list), 2)
        summary = Paragraph(
            f"<b>Data Summary:</b> Analyzed {len(weather_list)} locations. Average Hub Temperature: {avg_temp}°C.", styles['Normal'])
        elements.append(summary)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Babatunde_Abass_Report.pdf")


# THE CRITICAL BINDING FIX FOR RENDER
if __name__ == '__main__':
    # Render sets the PORT environment variable automatically
    port = int(os.environ.get("PORT", 10000))
    # Must bind to 0.0.0.0 to be visible to the public internet
    app.run(host='0.0.0.0', port=port)
