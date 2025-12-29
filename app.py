from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session, Response, redirect, url_for
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'babatunde_reliable_final_2025'

API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    error_msg = None
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        for city in cities:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()
                if response.get('cod') == 200:
                    # Accurate Local Time Calculation
                    offset = response['timezone']
                    local_dt = datetime.now(
                        timezone.utc) + timedelta(seconds=offset)

                    weather_data = {
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'local_time': local_dt.strftime("%I:%M %p")
                    }
                    weather_list.append(weather_data)
                else:
                    error_msg = f"City '{city}' not found in database."
            except Exception as e:
                error_msg = "Connection error with weather server."

        session['last_results'] = weather_list
        return render_template('index.html', weather_list=weather_list, report_date=report_date, error_msg=error_msg)

    return render_template('index.html')


@app.route('/clear')
def clear_session():
    session.clear()
    return redirect(url_for('index'))


@app.route('/download')
def download_report():
    results = session.get('last_results', [])
    if not results:
        return "No data", 400
    report_content = f"BABATUNDE ABASS | WEATHER ANALYSIS REPORT\n" + "="*45 + "\n"
    for w in results:
        report_content += f"{w['city']}: {w['temp']}°C | {w['desc'].capitalize()} | {w['local_time']}\n"
    return Response(report_content, mimetype="text/plain", headers={"Content-disposition": "attachment; filename=weather_report.txt"})


if __name__ == '__main__':
    app.run(debug=True)
