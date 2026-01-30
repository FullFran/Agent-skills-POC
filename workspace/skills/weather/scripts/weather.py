import sys
import json
import requests


def get_weather(city):
    try:
        # 1. Geocoding: Ciudad -> Lat/Lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=es&format=json"
        geo_resp = requests.get(geo_url, timeout=10)
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return {
                "summary": f"No pude encontrar la ciudad '{city}'.",
                "temperature": None,
            }

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location["name"]
        country = location.get("country", "")

        # 2. Weather: Lat/Lon -> Clima
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url, timeout=10)
        weather_data = weather_resp.json()

        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        windspeed = current.get("windspeed")

        return {
            "summary": f"En {name} ({country}) hace actualmente {temp}°C con vientos de {windspeed} km/h.",
            "temperature": temp,
        }

    except Exception as e:
        return {"summary": f"Error al obtener el clima: {str(e)}", "temperature": None}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"summary": "Falta la ciudad.", "temperature": None}))
        sys.exit(0)

    try:
        args = json.loads(sys.argv[1])
        city = args.get("city")
        if not city:
            print(
                json.dumps(
                    {"summary": "No se proporcionó ciudad.", "temperature": None}
                )
            )
        else:
            result = get_weather(city)
            print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"summary": f"Error fatal: {str(e)}", "temperature": None}))
