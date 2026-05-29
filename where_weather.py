# -*- coding: utf-8 -*-

import ctypes
import json
import os
import re
import sys
import threading
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from tkinter import ttk


UPDATE_INTERVAL_MS = 10 * 60 * 1000
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
CONFIG_PATH = APP_DIR / "config.json"
API_KEY_BAT_PATH = APP_DIR / "openweather_api_key.bat"
DEFAULT_CONFIG = {
    "location": "御茶ノ水,東京",
    "location_label": "御茶ノ水",
    "latitude": 35.6994,
    "longitude": 139.7657,
    "language": "ja",
}
PIXEL_FONT_DIR = RESOURCE_DIR / "fonts" / "PixelMplus" / "PixelMplus-20130602"
PIXEL_FONT_FILES = (
    PIXEL_FONT_DIR / "PixelMplus10-Regular.ttf",
    PIXEL_FONT_DIR / "PixelMplus10-Bold.ttf",
    PIXEL_FONT_DIR / "PixelMplus12-Regular.ttf",
    PIXEL_FONT_DIR / "PixelMplus12-Bold.ttf",
)
TITLE_ICON_PATH = RESOURCE_DIR / "assets" / "chick_icon.png"
WEATHER_ICON_DIR = RESOURCE_DIR / "assets" / "weather_icons"
FONT_FAMILY = "PixelMplus10"
TITLE_FONT_FAMILY = "PixelMplus12"
EMOJI_FONT_FAMILY = "Segoe UI Emoji"
FR_PRIVATE = 0x10
DPI_AWARENESS_SYSTEM_AWARE = 1
BACKGROUND_COLOR = "#050b07"
TEXT_COLOR = "#31d912"
MUTED_TEXT_COLOR = "#1ba24d"
TEMPERATURE_COLOR = "#9bd968"
SUPPORTED_LANGUAGES = ("ja", "en")
TEXT = {
    "ja": {
        "app_title": "イマドコ天気",
        "prompt": "イマドコ？",
        "change": "変更",
        "searching": "検索中",
        "searching_location": "場所を検索中...",
        "location_required": "場所を入力してください",
        "loading": "取得中...",
        "fetch_failed": "天気を取得できませんでした",
        "reload": "リロード",
        "topmost": "最前面",
        "language_toggle": "EN",
        "feels_like": "体感温度",
        "humidity": "湿度",
        "wind": "風速",
        "high_low": "最高 / 最低",
        "api_key_missing": "OPENWEATHER_API_KEY が未設定です",
        "api_key_invalid": "OpenWeatherMapのAPIキーを確認してください",
        "location_search_failed": "場所を検索できませんでした",
        "location_not_found": "場所が見つかりませんでした",
        "config_load_failed": "config.jsonを読み込めません",
    },
    "en": {
        "app_title": "Where Weather",
        "prompt": "Where?",
        "change": "Set",
        "searching": "Searching",
        "searching_location": "Searching...",
        "location_required": "Enter a location",
        "loading": "Loading...",
        "fetch_failed": "Could not get weather",
        "reload": "Reload",
        "topmost": "Top",
        "language_toggle": "日本語",
        "feels_like": "Feels like",
        "humidity": "Humidity",
        "wind": "Wind",
        "high_low": "High / Low",
        "api_key_missing": "OPENWEATHER_API_KEY is not set",
        "api_key_invalid": "Check your OpenWeatherMap API key",
        "location_search_failed": "Could not search location",
        "location_not_found": "Location not found",
        "config_load_failed": "Could not load config.json",
    },
}


def normalize_language(language):
    return language if language in SUPPORTED_LANGUAGES else "ja"


def text_for(language, key):
    return TEXT[normalize_language(language)][key]


def load_config():
    config = DEFAULT_CONFIG.copy()

    if not CONFIG_PATH.exists():
        return config

    try:
        with CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
            user_config = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{text_for(config.get('language', 'ja'), 'config_load_failed')}: {error}") from error

    config.update({key: value for key, value in user_config.items() if value is not None})
    config["language"] = normalize_language(config.get("language"))
    return config


def save_config(config):
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)
        file.write("\n")


CONFIG = load_config()
LOCATION = str(CONFIG["location"])
LOCATION_LABEL = str(CONFIG["location_label"])
LATITUDE = float(CONFIG["latitude"])
LONGITUDE = float(CONFIG["longitude"])
LANGUAGE = normalize_language(CONFIG["language"])


def get_api_key(language=LANGUAGE):
    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip().strip('"')
    if not api_key:
        api_key = load_api_key_from_bat()
    if not api_key:
        raise RuntimeError(text_for(language, "api_key_missing"))

    return api_key


def load_api_key_from_bat():
    if not API_KEY_BAT_PATH.exists():
        return ""

    try:
        content = API_KEY_BAT_PATH.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        content = API_KEY_BAT_PATH.read_text(encoding="cp932", errors="replace")
    except OSError:
        return ""

    match = re.search(r"set\s+\"OPENWEATHER_API_KEY=([^\"]+)\"", content, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def geocode_location(query, language):
    language = normalize_language(language)
    api_key = get_api_key(language)
    params = urllib.parse.urlencode(
        {
            "q": query,
            "limit": 1,
            "appid": api_key,
        }
    )
    url = f"https://api.openweathermap.org/geo/1.0/direct?{params}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "WhereWeather/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            results = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 401:
            raise RuntimeError(text_for(language, "api_key_invalid")) from error

        raise RuntimeError(f"{text_for(language, 'location_search_failed')}: {error.reason}") from error

    if not results:
        raise RuntimeError(text_for(language, "location_not_found"))

    result = results[0]
    local_names = result.get("local_names", {})
    label = local_names.get("ja") if language == "ja" else None
    label = label or result.get("name") or query
    state = result.get("state")
    country = result.get("country")
    display_parts = [label]

    if state and state != label:
        display_parts.append(state)
    if country:
        display_parts.append(country)

    return {
        "location": ", ".join(display_parts),
        "location_label": label,
        "latitude": result["lat"],
        "longitude": result["lon"],
        "language": language,
    }


def load_private_fonts():
    if not hasattr(ctypes, "windll"):
        return

    for font_path in PIXEL_FONT_FILES:
        if font_path.exists():
            ctypes.windll.gdi32.AddFontResourceExW(str(font_path), FR_PRIVATE, 0)


def enable_crisp_pixel_rendering():
    if not hasattr(ctypes, "windll"):
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(DPI_AWARENESS_SYSTEM_AWARE)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def choose_weather_icon(description):
    if any(word in description for word in ("雷", "雷雨", "thunder")):
        return "storm"
    if any(word in description for word in ("雪", "みぞれ", "sleet", "snow")):
        return "snow"
    if any(word in description for word in ("雨", "にわか雨", "霧雨", "rain", "drizzle")):
        return "rain"
    if any(word in description for word in ("曇", "くもり", "cloud", "overcast")):
        return "cloud"
    if any(word in description for word in ("晴", "快晴", "sunny", "clear")):
        return "sun"
    if any(word in description for word in ("霧", "もや", "fog", "mist")):
        return "fog"

    return "partly_cloudy"


def fetch_weather(latitude, longitude, language):
    language = normalize_language(language)
    api_key = get_api_key(language)
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}"
        f"&appid={api_key}&units=metric&lang={language}"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "WhereWeather/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        message = error.reason
        try:
            error_data = json.load(error)
            message = error_data.get("message", message)
        except Exception:
            pass

        if error.code == 401:
            raise RuntimeError(text_for(language, "api_key_invalid")) from error

        raise RuntimeError(f"OpenWeatherMapエラー: {message}") from error


def format_weather(data):
    weather = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})
    description = weather["description"]
    temp_min = round(main["temp_min"])
    temp_max = round(main["temp_max"])

    return {
        "icon": choose_weather_icon(description),
        "description": description,
        "temperature": f"{round(main['temp'])}℃",
        "feels_like": f"{round(main['feels_like'])}℃",
        "humidity": f"{main['humidity']}%",
        "wind": f"{round(wind.get('speed', 0) * 3.6)} km/h",
        "high_low": f"{temp_max}℃ / {temp_min}℃",
    }


class WhereWeatherApp(tk.Tk):
    def __init__(self):
        enable_crisp_pixel_rendering()
        super().__init__()

        self.config_data = CONFIG.copy()
        self.location_label = LOCATION_LABEL
        self.latitude = LATITUDE
        self.longitude = LONGITUDE
        self.language = LANGUAGE

        self.title(f"Where Weather - {self.location_label}")
        self.geometry("360x400+40+40")
        self.minsize(360, 400)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(bg=BACKGROUND_COLOR)
        load_private_fonts()
        self._set_title_icon()

        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging_window = False
        self._refresh_job = None
        self._is_fetching = False
        self._is_changing_location = False
        self.weather_icon_images = self._load_weather_icons()

        self._build_ui()
        self._bind_drag_events()
        self.refresh_weather()

    def _set_title_icon(self):
        if not TITLE_ICON_PATH.exists():
            return

        self._title_icon = tk.PhotoImage(file=str(TITLE_ICON_PATH))
        self.iconphoto(True, self._title_icon)

    def _load_weather_icons(self):
        icon_names = (
            "partly_cloudy",
            "cloud",
            "sun",
            "rain",
            "snow",
            "storm",
            "fog",
            "loading",
            "error",
        )
        return {
            name: tk.PhotoImage(file=str(WEATHER_ICON_DIR / f"{name}.png"))
            for name in icon_names
            if (WEATHER_ICON_DIR / f"{name}.png").exists()
        }

    def t(self, key):
        return text_for(self.language, key)

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Widget.TFrame", background=BACKGROUND_COLOR)
        style.configure(
            "Title.TLabel",
            background=BACKGROUND_COLOR,
            foreground=TEXT_COLOR,
            font=(TITLE_FONT_FAMILY, -24, "bold"),
        )
        style.configure(
            "Value.TLabel",
            background=BACKGROUND_COLOR,
            foreground=TEXT_COLOR,
            font=(FONT_FAMILY, -21),
        )
        style.configure(
            "Small.TLabel",
            background=BACKGROUND_COLOR,
            foreground=MUTED_TEXT_COLOR,
            font=(FONT_FAMILY, -12),
        )
        style.configure(
            "Prompt.TLabel",
            background=BACKGROUND_COLOR,
            foreground=TEXT_COLOR,
            font=(FONT_FAMILY, -14),
        )
        style.configure(
            "Action.TButton",
            background="#07150a",
            foreground=TEXT_COLOR,
            font=(FONT_FAMILY, -14),
            padding=(8, 4),
        )
        style.map(
            "Action.TButton",
            background=[("active", "#0c2712")],
            foreground=[("active", TEMPERATURE_COLOR)],
        )
        style.configure(
            "Pixel.TCheckbutton",
            background=BACKGROUND_COLOR,
            foreground=TEXT_COLOR,
            font=(FONT_FAMILY, -14),
        )
        style.map(
            "Pixel.TCheckbutton",
            background=[("active", BACKGROUND_COLOR)],
            foreground=[("active", TEMPERATURE_COLOR)],
        )

        root = ttk.Frame(self, style="Widget.TFrame", padding=12)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root, style="Widget.TFrame")
        header.pack(fill="x")

        self.title_label = ttk.Label(header, text=self.t("app_title"), style="Title.TLabel")
        self.title_label.pack(side="left", anchor="w")

        self.location_prompt_label = ttk.Label(root, text=self.t("prompt"), style="Prompt.TLabel")
        self.location_prompt_label.pack(anchor="w", pady=(10, 2))

        location_row = ttk.Frame(root, style="Widget.TFrame")
        location_row.pack(fill="x")

        self.location_var = tk.StringVar(value=self.location_label)
        self.location_entry = tk.Entry(
            location_row,
            textvariable=self.location_var,
            bg="#07150a",
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="solid",
            bd=1,
            highlightbackground=TEXT_COLOR,
            highlightcolor=TEMPERATURE_COLOR,
            highlightthickness=1,
            font=(FONT_FAMILY, -14),
        )
        self.location_entry.pack(side="left", fill="x", expand=True, ipady=3)
        self.location_entry.bind("<Return>", lambda _event: self.change_location())

        self.location_button = tk.Button(
            location_row,
            text=self.t("change"),
            command=self.change_location,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            activebackground="#0c2712",
            activeforeground=TEMPERATURE_COLOR,
            bd=2,
            relief="solid",
            highlightbackground=TEXT_COLOR,
            highlightcolor=TEXT_COLOR,
            highlightthickness=1,
            font=(FONT_FAMILY, -14),
            padx=8,
            pady=2,
        )
        self.location_button.pack(side="left", padx=(8, 0))

        self.description_label = ttk.Label(root, text=self.t("loading"), style="Value.TLabel")
        self.description_label.pack(anchor="w", pady=(12, 6))

        current_row = ttk.Frame(root, style="Widget.TFrame")
        current_row.pack(fill="x", anchor="w")

        self.chick_image = tk.PhotoImage(file=str(TITLE_ICON_PATH))
        self.chick_label = tk.Label(
            current_row,
            image=self.chick_image,
            bg=BACKGROUND_COLOR,
            bd=0,
            highlightthickness=0,
        )
        self.chick_label.pack(side="left", anchor="center", padx=(0, 6))

        self.icon_label = tk.Label(
            current_row,
            image=self.weather_icon_images.get("partly_cloudy"),
            bg=BACKGROUND_COLOR,
            bd=0,
            highlightthickness=0,
        )
        self.icon_label.pack(side="left", anchor="center", padx=(0, 8))

        self.temperature_label = ttk.Label(
            current_row,
            text="--℃",
            background=BACKGROUND_COLOR,
            foreground=TEMPERATURE_COLOR,
            font=(FONT_FAMILY, -48, "bold"),
        )
        self.temperature_label.pack(side="left", anchor="center")

        self.detail_label = ttk.Label(root, text="", style="Value.TLabel", justify="left")
        self.detail_label.pack(anchor="w", pady=(16, 8))

        button_row = ttk.Frame(root, style="Widget.TFrame")
        button_row.pack(fill="x", side="bottom")

        self.refresh_button = tk.Button(
            button_row,
            text=self.t("reload"),
            command=self.refresh_weather,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            activebackground="#0c2712",
            activeforeground=TEMPERATURE_COLOR,
            bd=2,
            relief="solid",
            highlightbackground=TEXT_COLOR,
            highlightcolor=TEXT_COLOR,
            highlightthickness=1,
            font=(FONT_FAMILY, -14),
            padx=10,
            pady=3,
        )
        self.refresh_button.pack(side="left")

        self.language_button = tk.Button(
            button_row,
            text=self.t("language_toggle"),
            command=self.toggle_language,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            activebackground="#0c2712",
            activeforeground=TEMPERATURE_COLOR,
            bd=2,
            relief="solid",
            highlightbackground=TEXT_COLOR,
            highlightcolor=TEXT_COLOR,
            highlightthickness=1,
            font=(FONT_FAMILY, -14),
            padx=8,
            pady=3,
        )
        self.language_button.pack(side="left", padx=(8, 0))

        topmost_check = ttk.Checkbutton(
            button_row,
            text=self.t("topmost"),
            command=self.toggle_topmost,
            style="Pixel.TCheckbutton",
        )
        topmost_check.state(["selected"])
        topmost_check.pack(side="right")
        self.topmost_check = topmost_check

    def _bind_drag_events(self):
        for widget in (
            self.title_label,
            self.location_prompt_label,
            self.description_label,
            self.chick_label,
            self.icon_label,
            self.temperature_label,
        ):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag)
            widget.bind("<ButtonRelease-1>", self._stop_drag)

    def _start_drag(self, event):
        self._is_dragging_window = True
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _drag(self, event):
        if not self._is_dragging_window:
            return

        x = self.winfo_x() + event.x - self._drag_start_x
        y = self.winfo_y() + event.y - self._drag_start_y
        self.geometry(f"+{x}+{y}")

    def _stop_drag(self, _event):
        self._is_dragging_window = False

    def toggle_topmost(self):
        self.attributes("-topmost", self.topmost_check.instate(["selected"]))

    def toggle_language(self):
        self.language = "en" if self.language == "ja" else "ja"
        self.config_data["language"] = self.language
        save_config(self.config_data)
        self._refresh_texts()
        self.refresh_weather()

    def _refresh_texts(self):
        self.title_label.configure(text=self.t("app_title"))
        self.location_prompt_label.configure(text=self.t("prompt"))
        self.location_button.configure(text=self.t("change"))
        self.refresh_button.configure(text=self.t("reload"))
        self.language_button.configure(text=self.t("language_toggle"))
        self.topmost_check.configure(text=self.t("topmost"))

    def refresh_weather(self):
        if self._is_fetching:
            return

        self._is_fetching = True
        self.icon_label.configure(image=self.weather_icon_images.get("loading"))

        thread = threading.Thread(target=self._fetch_weather_in_background, daemon=True)
        thread.start()

    def _fetch_weather_in_background(self):
        try:
            weather = format_weather(fetch_weather(self.latitude, self.longitude, self.language))
            self.after(0, lambda: self._show_weather(weather))
        except Exception as error:
            self.after(0, lambda error=error: self._show_error(error))

    def change_location(self):
        if self._is_changing_location:
            return

        query = self.location_var.get().strip()
        if not query:
            self.description_label.configure(text=self.t("location_required"))
            return

        self._is_changing_location = True
        self.location_button.configure(text=self.t("searching"), state="disabled")
        self.description_label.configure(text=self.t("searching_location"))

        thread = threading.Thread(target=self._change_location_in_background, args=(query,), daemon=True)
        thread.start()

    def _change_location_in_background(self, query):
        try:
            new_config = geocode_location(query, self.language)
            save_config(new_config)
            self.after(0, lambda: self._apply_location(new_config))
        except Exception as error:
            self.after(0, lambda error=error: self._show_location_error(error))

    def _apply_location(self, new_config):
        self.config_data = new_config
        self.location_label = str(new_config["location_label"])
        self.latitude = float(new_config["latitude"])
        self.longitude = float(new_config["longitude"])
        self.language = normalize_language(new_config.get("language", self.language))
        self.location_var.set(self.location_label)
        self.title(f"Where Weather - {self.location_label}")
        self._refresh_texts()
        self._finish_location_change()
        self.refresh_weather()

    def _show_location_error(self, error):
        self.description_label.configure(text=str(error))
        self._finish_location_change()

    def _finish_location_change(self):
        self._is_changing_location = False
        self.location_button.configure(text=self.t("change"), state="normal")

    def _show_weather(self, weather):
        self._is_fetching = False
        self.icon_label.configure(image=self.weather_icon_images.get(weather["icon"]))
        self.description_label.configure(text=weather["description"])
        self.temperature_label.configure(text=weather["temperature"])
        self.detail_label.configure(
            text=(
                f"{self.t('feels_like')}: {weather['feels_like']}\n"
                f"{self.t('humidity')}: {weather['humidity']}\n"
                f"{self.t('wind')}: {weather['wind']}\n"
                f"{self.t('high_low')}: {weather['high_low']}"
            )
        )
        self._schedule_next_refresh()

    def _show_error(self, error):
        self._is_fetching = False
        self.icon_label.configure(image=self.weather_icon_images.get("error"))
        self.description_label.configure(text=self.t("fetch_failed"))
        self._schedule_next_refresh()

    def _schedule_next_refresh(self):
        if self._refresh_job is not None:
            self.after_cancel(self._refresh_job)

        self._refresh_job = self.after(UPDATE_INTERVAL_MS, self.refresh_weather)


if __name__ == "__main__":
    app = WhereWeatherApp()
    app.mainloop()
