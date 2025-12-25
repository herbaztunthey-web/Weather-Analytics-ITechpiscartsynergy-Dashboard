from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURATION (Check these carefully!) ---
API_KEY = os.getenv('WEATHER_API_KEY')
CITIES = ['Lagos', 'London', 'New York']
SENDER_EMAIL = os.getenv('EMAIL_USER')
SENDER_PASSWORD = os.getenv('EMAIL_PASS')
RECEIVER_EMAIL = "tunthey@yahoo.com"


def get_weather_summary():
    report_html = ""
    count = 0

    for city in CITIES:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()

            if data.get('cod') == 200:
                temp = data['main']['temp']
                desc = data['weather'][0]['description']

                # --- NEW LOGIC STARTS HERE ---
                if temp > 30:
                    tip = "Stay hydrated, it's hot!"
                elif temp < 20:
                    tip = "Might need a sweater today."
                else:
                    tip = "Enjoy the pleasant weather!"
                # --- NEW LOGIC ENDS HERE ---

                report_html += f"<li><b>{city}:</b> {temp}°C, {desc.capitalize()}. <i>Note: {tip}</i></li>"
                count += 1
        except Exception as e:
            print(f"Error: {e}")

    return report_html, count


def send_email():
    content, count = get_weather_summary()
    date_str = datetime.now().strftime("%d %b %Y")

    if count == 0:
        print("No weather data found. Email not sent to avoid blank report.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = f"Daily Weather Briefing: {date_str}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    # THE HTML BODY
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #1e3799;">Babatunde Abass Analytics</h2>
        <p>Weather report for <b>{date_str}</b>:</p>
        <ul style="background: #f4f4f4; padding: 20px; border-radius: 10px;">
            {content}
        </ul>
        <br>
        <p style="font-size: 11px; color: gray;">Automated Data Pipeline - VS Code Project</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Success! Email sent with {count} cities.")
    except Exception as e:
        print(f"SMTP Error: {e}")


if __name__ == "__main__":
    send_email()
