import requests
import random

# 1. Configuration
API_KEY = "aad4cbdae56d6d693c4f99064fe46dcd"


# 2. Expanded Global Pools
OCEANIA = ["Auckland", "Wellington", "Sydney",
           "Melbourne", "Brisbane", "Perth"]
SCANDINAVIA = ["Oslo", "Bergen", "Stockholm", "Gothenburg", "Malmo", "Uppsala"]
NORTH_AMERICA = ["Toronto", "Vancouver", "Montreal", "Ottawa", "Calgary"]
AFRICA = ["Lagos", "Ibadan", "Abuja", "Nairobi", "Cairo"]
ASIA = ["Abu Dhabi", "Tokyo", "Shanghai", "Singapore", "Seoul"]


def generate_global_viral_post():
    # Pick 1 random city from each specialized region
    selection = [
        random.choice(OCEANIA),
        random.choice(SCANDINAVIA),
        random.choice(NORTH_AMERICA),
        random.choice(AFRICA),
        random.choice(ASIA)
    ]

    print("🌎 --- GLOBAL WEATHER ROUNDUP --- 🌎\n")

    for city in selection:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if data.get("cod") == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].title()

            print(f"📍 {city.upper()}")
            print(f"   Vibe: {desc} | Temp: {temp}°C")
            # Viral hook logic
            if temp < 0:
                print("   ❄️ Content Idea: 'Winter is here! Who else is freezing?'")
            elif temp > 30:
                print("   🔥 Content Idea: 'Heatwave alert! Stay cool out there.'")
            else:
                print("   ✨ Content Idea: 'Perfect weather for a walk today.'")
            print("-" * 35)

    print("\n#GlobalWeather #TechHustle #PythonDev #TravelLife")


generate_global_viral_post()
