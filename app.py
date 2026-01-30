from flask import Flask, render_template

app = Flask(__name__)

# 1. The Hub (Main Entry Point)


@app.route('/')
def home():
    return render_template('index.html')

# 2. The Weather Module


@app.route('/weather')
def weather():
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
    app.run(debug=True)
