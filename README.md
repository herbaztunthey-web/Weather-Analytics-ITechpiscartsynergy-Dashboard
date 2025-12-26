# 🌦️ Weather-Analytics-ITechpiscartsynergy-Dashboard

![Status](https://img.shields.io/badge/Render-Live-brightgreen)

## 🚀 Live Demo
You can view the live, fully functional version of this dashboard here:
**[View Live Demo](https://weather-analytics-itechpiscartsynergy-dashboard.onrender.com/)**

---

## ✨ Features
* **Real-Time Data Retrieval:** Instant weather updates for any city worldwide using the OpenWeatherMap API.
* **Comprehensive Metrics:** Displays temperature, humidity, wind speed, and atmospheric conditions.
* **Responsive Design:** A clean, professional dashboard interface that works on mobile, tablet, and desktop.
* **Dynamic Search:** Intuitive search bar with real-time feedback.
* **Cloud Hosted:** Fully deployed on Render with an automated CI/CD pipeline from GitHub.

---

## 🧠 How It Works
1. **User Input:** The user enters a city name into the search bar.
2. **Backend Processing:** Flask captures the request and calls the OpenWeatherMap API using a secure `WEATHER_API_KEY`.
3. **Data Parsing:** The Python backend parses the JSON response to extract key analytics.
4. **Front-End Rendering:** Flask injects the data into a responsive HTML template for the user to view.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Framework:** Flask
* **Server:** Gunicorn
* **Deployment:** Render
* **Data Source:** OpenWeatherMap API

---

## ⚙️ Local Setup
To run this project on your own machine:

1. **Clone the repository**
   ```bash
   git clone [https://github.com/herbaztunthey-web/Weather-Analytics-ITechpiscartsynergy-Dashboard.git](https://github.com/herbaztunthey-web/Weather-Analytics-ITechpiscartsynergy-Dashboard.git)

## Install dependencies  
   pip install -r requirements.txt
## Configure Environment Create a .env file and add: WEATHER_API_KEY=your_key_here
## Run the app
   python app.py

