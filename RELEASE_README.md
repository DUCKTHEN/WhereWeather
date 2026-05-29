# WhereWeather

WhereWeather is a small Windows desktop weather widget.
Type a location to check the weather there, and switch between Japanese and English.

WhereWeatherは、好きな場所の天気を表示できるWindows用の小さなデスクトップウィジェットです。

## Setup

1. Create your own OpenWeatherMap API key:
   https://openweathermap.org/api
2. Copy `openweather_api_key.example.bat`.
3. Rename the copied file to `openweather_api_key.bat`.
4. Open `openweather_api_key.bat` and replace `your_api_key_here` with your API key.
5. Double-click `WhereWeather.exe`.

```bat
set "OPENWEATHER_API_KEY=your_api_key_here"
```

## 使い方

1. OpenWeatherMapで自分のAPIキーを取得します。
2. `openweather_api_key.example.bat` をコピーします。
3. コピーしたファイル名を `openweather_api_key.bat` に変更します。
4. `your_api_key_here` を自分のAPIキーに置き換えます。
5. `WhereWeather.exe` をダブルクリックします。

## Notes

- `WhereWeather.exe` is for Windows.
- Do not share your `openweather_api_key.bat`.
- Type a location and press `Set` / `変更`.
- Use `EN` / `日本語` to switch languages.
- If `config.json` does not exist, the app starts with the default Ochanomizu location.

## 注意

- `WhereWeather.exe` はWindows用です。
- 自分の `openweather_api_key.bat` は共有しないでください。
- 場所を入力して `Set` / `変更` を押すと天気を更新できます。
- `EN` / `日本語` ボタンで表示言語を切り替えられます。
