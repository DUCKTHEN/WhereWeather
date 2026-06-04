# WhereWeather
<img width="188" height="229" alt="image" src="https://github.com/user-attachments/assets/7d205653-7aaf-4ba4-99f4-5c53f63869a1" />
<img width="188" height="229" alt="image" src="https://github.com/user-attachments/assets/220b695d-72cc-40b7-9fe1-bc81d4014a57" />

WhereWeatherは、場所を入力してその地点の天気を表示できるWindows用の小さなデスクトップウィジェットです。
OpenWeatherMapから天気を取得し、日本語 / English の表示切り替えができます。

WhereWeather is a tiny retro desktop weather widget for Windows.
Type a location, check the weather there, and switch the UI between Japanese and English.

## Feedback

不具合報告や質問はGitHub Issuesからお願いします。
Please use GitHub Issues for bug reports, questions, and feedback.

## 使い方

1. `WhereWeather.exe` と同じフォルダにある `openweather_api_key.example.bat` をコピーします。
2. コピーしたファイル名を `openweather_api_key.bat` に変更します。
3. `openweather_api_key.bat` を開き、`your_api_key_here` を自分のOpenWeatherMap APIキーに置き換えます。
4. `WhereWeather.exe` をダブルクリックして起動します。

```bat
set "OPENWEATHER_API_KEY=取得したAPIキー"
```

WhereWeatherは、`WhereWeather.exe` と同じフォルダにある `openweather_api_key.bat` と `config.json` を読み込みます。
初回起動時に `config.json` がない場合は、御茶ノ水の設定で起動します。

## Quick Start

1. Copy `openweather_api_key.example.bat` in the same folder as `WhereWeather.exe`.
2. Rename the copied file to `openweather_api_key.bat`.
3. Open `openweather_api_key.bat` and replace `your_api_key_here` with your own OpenWeatherMap API key.
4. Double-click `WhereWeather.exe`.

```bat
set "OPENWEATHER_API_KEY=your_api_key_here"
```

WhereWeather reads `openweather_api_key.bat` and `config.json` from the same folder as `WhereWeather.exe`.
If `config.json` does not exist, the app starts with the default Ochanomizu location.

## APIキーについて

WhereWeatherは天気データの取得にOpenWeatherMapを使います。
利用する人それぞれが、自分のOpenWeatherMap APIキーを用意してください。

[OpenWeatherMap](https://openweathermap.org/api) でアカウントを作成するとAPIキーを取得できます。

`openweather_api_key.bat` は個人用の秘密情報です。
GitHubなどで公開する場合も、本物のAPIキーを書いたファイルはアップロードしないでください。

## API Key

WhereWeather uses OpenWeatherMap for weather data.
Each user should create and use their own OpenWeatherMap API key.

Do not upload a real `openweather_api_key.bat` file to GitHub.
Only `openweather_api_key.example.bat` should be shared.

## 場所と言語

ウィジェット内の入力欄に場所を入力して、`変更` を押すと表示場所を変更できます。
入力した場所はOpenWeatherMapで検索され、緯度経度に変換して `config.json` に保存されます。

下部の `EN` / `日本語` ボタンで、日本語表示と英語表示を切り替えられます。

`config.json` を直接編集することもできます。初期値は次の内容です。

```json
{
  "location": "御茶ノ水,東京",
  "location_label": "御茶ノ水",
  "latitude": 35.6994,
  "longitude": 139.7657,
  "language": "ja"
}
```

`language` は `ja` または `en` を指定できます。

## Location and Language

Enter a location in the widget and press `Set` to update the weather location.
The app searches the location with OpenWeatherMap, converts it to latitude and longitude, and saves it to `config.json`.

Use the `EN` / `日本語` button to switch between Japanese and English.

You can also edit `config.json` directly.
Set `language` to `ja` or `en`.

## Pythonで起動する場合

ソースコードから起動する場合は、Python 3をインストールしてから次のバッチファイルを実行します。

```bat
start_where_weather.bat
```

配布している `WhereWeather.exe` はWindows用です。
macOSでは、Python 3を使ってソースコードから起動してください。

```bash
python3 where_weather.py
```

Mac用の `.app` を配布する場合は、基本的にmacOS上で別途ビルドする必要があります。

## Running from Source

The provided `WhereWeather.exe` is for Windows.
On macOS, run the app from source with Python 3:

```bash
python3 where_weather.py
```

A macOS `.app` build should generally be created on macOS.

## exeを作る場合

配布用のWindows exeを作る場合は、PyInstallerをインストールしてから `build_where_weather.bat` を実行します。

```bat
python -m pip install pyinstaller
build_where_weather.bat
```

成功すると `dist` フォルダに `WhereWeather.exe` が作られます。
`dist` には配布用READMEとexampleファイルもコピーされます。

## License

WhereWeather is released under the MIT License.

This repository includes PixelMplus fonts, which are distributed under the M+ FONT LICENSE.
See `THIRD_PARTY_NOTICES.md` and the license files under `fonts/` for details.
