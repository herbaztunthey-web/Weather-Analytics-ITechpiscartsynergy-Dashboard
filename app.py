import os
from flask import Flask, render_template

app = Flask(__name__)

# 1. The Hub (Main Entry Point)


@app.route('/')
def home():
    return render_template('index.html')

# 2. The Weather Module (Updated for Global Data)


@app.route('/weather')
def weather():
    # This is where we will eventually pass our API data
    return render_template('weather.html')

# 3. The Maritime Module


@app.route('/maritime')
def maritime():
    return render_template('maritime.html')

# 4. The Solar Module


@app.route('/solar')
def solar():
    return render_template('solar.html')


if __name__ == '__main__':
    # RENDER REQUIREMENT: Use the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
