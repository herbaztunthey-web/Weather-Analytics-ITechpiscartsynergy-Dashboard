from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session, Response, redirect, url_for
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'babatunde_premium_v8'

API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    stats = {}
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        for city in cities:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()
                if response.get('cod') == 200:
                    weather_data = {
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'local_time': (datetime.now(timezone.utc) + timedelta(seconds=response['timezone'])).strftime("%I:%M %p")
                    }
                    weather_list.append(weather_data)
            except:
                pass

        if weather_list:
            stats['hottest'] = max(
                weather_list, key=lambda x: x['temp'])['city']
            stats['coldest'] = min(
                weather_list, key=lambda x: x['temp'])['city']
            stats['avg_temp'] = round(
                sum(d['temp'] for d in weather_list) / len(weather_list), 1)

        session['last_results'] = weather_list
        return render_template('index.html', weather_list=weather_list, report_date=report_date, stats=stats)

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
    report_content = f"WEATHER ANALYSIS - BABATUNDE ABASS\n" + "="*40 + "\n"
    for w in results:
        report_content += f"{w['city']}: {w['temp']}°C | {w['desc']}\n"
    return Response(report_content, mimetype="text/plain", headers={"Content-disposition": "attachment; filename=report.txt"})


if __name__ == '__main__':
    app.run(debug=True)
