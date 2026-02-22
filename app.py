import os
import io
import requests
import sqlite3  # Needed for history
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

# --- AI BRAIN IMPORTS ---
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

app = Flask(__name__)
app.secret_key = "babatunde_abass_hub_2026"

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
DB_PATH = "final_weather.db"
VECTOR_DB_DIR = "ai_brain/vector_store"


def get_ai_insight(city_name):
    """Safe helper to ask the brain for history without crashing the app"""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = Chroma(persist_directory=VECTOR_DB_DIR,
                    embedding_function=embeddings)
        # Search for 1 relevant historical record
        results = db.similarity_search(city_name, k=1)
        if results:
            return results[0].page_content
    except Exception as e:
        print(f"AI Brain Sleep: {e}")
    return "No historical records found for this city."


@app.route('/')
def home():
    if 'weather_list' not in session:
        session['weather_list'] = []
    return render_template('index.html', weather_list=session['weather_list'])


@app.route('/analyze', methods=['POST'])
def analyze():
    session['weather_list'] = []
    raw_cities = request.form.get('city')
    units = request.form.get('unit', 'metric')

    # Mapping for the Brain only (Protects your format)
    unit_label = "°C" if units == "metric" else "°F"

    city_names = [c.strip() for c in raw_cities.split(',') if c.strip()]
    weather_list = []
    ai_insights = []  # New bucket for AI talk

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for city in city_names:
        params = {'q': city, 'appid': API_KEY, 'units': units}
        try:
            response = requests.get(BASE_URL, params=params).json()
            if response.get('cod') == 200:
                name = response['name']
                temp = response['main']['temp']
                desc = response['weather'][0]['description'].capitalize()

                # 1. ADD TO AI INSIGHTS (BEFORE SAVING NEW DATA)
                insight = get_ai_insight(name)
                ai_insights.append({"city": name, "text": insight})

                # 2. SAVE TO SQL (WITH CLEAN UNIT)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO history (city, temp, timestamp, unit) VALUES (?, ?, ?, ?)",
                               (name, temp, timestamp, unit_label))

                new_city_data = {
                    'city': name,
                    'temp': temp,
                    'desc': desc,
                    'icon': response['weather'][0]['icon'],
                    'lat': response['coord']['lat'],
                    'lon': response['coord']['lon']
                }
                weather_list.append(new_city_data)
        except Exception as e:
            print(f"Error fetching {city}: {e}")

    conn.commit()
    conn.close()

    session['weather_list'] = weather_list
    session.permanent = True
    session.modified = True

    return render_template('index.html', weather_list=weather_list, ai_insights=ai_insights)

# ... (Keep your download_pdf and main block exactly the same) ...
