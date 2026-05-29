# WhereWeather

WhereWeatherは、場所を入力してその地点の天気を表示できるWindows用の小さなデスクトップウィジェットです。
OpenWeatherMapから天気を取得し、日本語 / English の表示切り替えができます。

## Feedback

不具合報告や質問はGitHub Issuesからお願いします。

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

## APIキーについて

WhereWeatherは天気データの取得にOpenWeatherMapを使います。
利用する人それぞれが、自分のOpenWeatherMap APIキーを用意してください。

[OpenWeatherMap](https://openweathermap.org/api) でアカウントを作成するとAPIキーを取得できます。

`openweather_api_key.bat` は個人用の秘密情報です。
GitHubなどで公開する場合も、本物のAPIキーを書いたファイルはアップロードしないでください。

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

## Pythonで起動する場合

ソースコードから起動する場合は、Python 3をインストールしてから次のバッチファイルを実行します。

```bat
start_where_weather.bat
```

## exeを作る場合

配布用のWindows exeを作る場合は、PyInstallerをインストールしてから `build_where_weather.bat` を実行します。

```bat
python -m pip install pyinstaller
build_where_weather.bat
```

成功すると `dist` フォルダに `WhereWeather.exe` が作られます。
`dist` にはREADMEとexampleファイルもコピーされます。

## License

MIT License
