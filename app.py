from datetime import datetime, timezone, timedelta
import requests
from flask import Flask, render_template, request, session, Response
import os
import geonamescache
from dotenv import load_dotenv

# Load your .env file containing the WEATHER_API_KEY
load_dotenv()
app = Flask(__name__)

# This key is required for Search History and Download functionality
app.secret_key = 'babatunde_ultra_clear_2025'

API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    error_msg = None
    report_date = datetime.now().strftime("%B %d, %Y | %H:%M")

    # Initialize search history in session
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        # Support for multi-city search (e.g., Lagos, London, Tokyo)
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        gc = geonamescache.GeonamesCache()
        continent_map = {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
            'SA': 'South America', 'OC': 'Oceania', 'AN': 'Antarctica'
        }

        for city in cities:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()

                # Check for successful API response
                if response.get('cod') == 200:
                    # 1. Precise Local Time Logic
                    offset = response['timezone']
                    local_dt = datetime.now(
                        timezone.utc) + timedelta(seconds=offset)

                    # 2. Unique Flag Mapping (Using ISO codes)
                    country_code = response['sys']['country'].lower()
                    country_info = gc.get_countries().get(country_code.upper())
                    continent_name = continent_map.get(country_info.get(
                        'continentcode'), "Global") if country_info else "Global"

                    weather_data = {
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                        'local_time': local_dt.strftime("%I:%M %p"),
                        'continent': continent_name,
                        'country_code': country_code  # Sent to HTML for background flags
                    }
                    weather_list.append(weather_data)

                    # 3. Update Search History (Keep top 5)
                    if response['name'] not in session['history']:
                        session['history'].insert(0, response['name'])
                        session['history'] = session['history'][:5]
                        session.modified = True
                else:
                    error_msg = f"System Error: City '{city}' not found in global database."

            except Exception as e:
                error_msg = "Network Error: Could not reach weather servers."

        # Save results in session for the Download Report feature
        session['last_results'] = weather_list
        return render_template('index.html', weather_list=weather_list, report_date=report_date, error_msg=error_msg, history=session['history'])

    return render_template('index.html', history=session['history'])


@app.route('/download')
def download_report():
    results = session.get('last_results', [])
    if not results:
        return "No data available for download. Please perform a search first.", 400

    # Building the professional text report
    report_content = f"BABATUNDE ABASS | GLOBAL WEATHER ANALYTICS\n"
    report_content += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report_content += "="*50 + "\n"
    for w in results:
        report_content += f"LOCATION: {w['city']} ({w['continent']})\n"
        report_content += f"LOCAL TIME: {w['local_time']}\n"
        report_content += f"TEMPERATURE: {w['temp']}°C\n"
        report_content += f"CONDITIONS: {w['desc'].capitalize()}\n"
        report_content += f"HUMIDITY: {w['humidity']}%\n"
        report_content += "-"*30 + "\n"

    return Response(
        report_content,
        mimetype="text/plain",
        headers={
            "Content-disposition": "attachment; filename=Babatunde_Weather_Report.txt"}
    )


if __name__ == '__main__':
    app.run(debug=True)
