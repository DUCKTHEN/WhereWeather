import json
import os
import urllib.error
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
CONFIG_EXAMPLE_PATH = BASE_DIR / "config.example.json"


def load_location_config():
    path = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_EXAMPLE_PATH

    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def main():
    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip().strip('"')
    config = load_location_config()
    latitude = config["latitude"]
    longitude = config["longitude"]
    location_label = config["location_label"]
    language = config.get("language", "ja")

    print(f"OPENWEATHER_API_KEY: {'set' if api_key else 'missing'}")
    print(f"length: {len(api_key)}")
    print(f"location: {location_label} ({latitude}, {longitude})")
    print(f"language: {language}")

    if not api_key:
        return

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}"
        f"&appid={api_key}&units=metric&lang={language}"
    )

    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        print(f"HTTP {error.code}")
        print(body)
        return

    weather = data["weather"][0]["description"]
    temp = round(data["main"]["temp"])
    print("OK")
    print(f"{weather} / {temp}℃")


if __name__ == "__main__":
    main()
