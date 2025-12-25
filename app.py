from datetime import datetime  # Crucial for the report date
import requests
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

# --- YOUR CONFIGURATION ---
API_KEY = os.getenv('WEATHER_API_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_list = []
    # Create the date timestamp immediately
    current_time = datetime.now().strftime("%B %d, %Y | %H:%M")

    if request.method == 'POST':
        city_input = request.form.get('city', '')
        # Split cities by comma and clean them
        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        for city in cities:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            try:
                response = requests.get(url).json()
                if response.get('cod') == 200:
                    weather_list.append({
                        'city': response['name'],
                        'temp': response['main']['temp'],
                        'humidity': response['main']['humidity'],
                        'desc': response['weather'][0]['description'],
                        'icon': response['weather'][0]['icon'],
                    })
            except Exception as e:
                print(f"Error fetching {city}: {e}")

        # Return the results WITH the report_date
        return render_template('index.html', weather_list=weather_list, report_date=current_time)

    # Initial page load
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
