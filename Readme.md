# Raspi Pico W RSS Display

Raspberry Pi Pico WでRSSサイトにアクセスし、記事のタイトルと概要をディスプレイに表示するプログラムです。

This program is designed to sequentially display the titles and summaries of articles from an RSS website using Raspberry Pi Pico W and an OLED display.

## 機能概要

- プログラム内で指定したRSSサイトにアクセスし、タイトルと記事の概要を順次表示します
- タクトスイッチを押すとフォントサイズが切り替わります(3段階)

## 使用パーツ

- Raspberry Pi Pico WH … 1,518円（税込）
- 有機ELディスプレイ SSD1306 … 580円（税込）
- タクトスイッチ … 30円（税込）
- ブレッドボード … 449円（税込）
- 配線用のワイヤー

合計：2,577円（税込）

## 配線図

<img src="https://github.com/led-mirage/RaspiPicoW-RSSDisplay/assets/139528700/b0e6df4f-4e0d-4a36-9acb-897446c70daf" alt="配線図" width="500">

## 実行画面

https://github.com/led-mirage/RaspiPicoW-RSSDisplay/assets/139528700/15349fb8-4f12-49a9-a633-08aec476a31c

## 開発環境

- Thonny 4.0.2
- Windows 10 / 11

## 実行環境

- Raspberry Pi Pico
- MicroPython v1.20.0

## インストール

PCとRaspberry Pi Pico Wを接続して、以下のファイルをPicoにコピーしてください。Thonnyを使うと簡単です。

```
  main.py [メインプログラム]
  ssd1306.py [ssd1306用ドライバ]
  ssd1306_mfont.py [ssd1306用ドライバ拡張]
  mfont [フォントライブラリ（外部ライブラリ）]
    │  mfont.py [フォントドライバモジュール]
    │  tma_jp_utl.py [フォントモジュール用サブルーチン]
    │  __init__.py [フォントドライバモジュール用]
    └─ fonts [フォントファイル]
            u_12x12.fnt [東雲フォント(12ドット)]
            u_14x14.fnt [東雲フォント(14ドット)]
            u_16x16.fnt [東雲フォント(16ドット)]
```

※mfontフォルダ以下はTamakichiさん作成のライブラリです。  
以下のリンクから別途ダウンロードしてください。  
https://github.com/Tamakichi/pico_MicroPython_Multiifont  
fontsフォルダのフォントは、オリジナルのフォルダの中から12、14、16ドットフォントを抜粋してインストールします。

## WiFiアクセスポイントの設定

main.pyの先頭部分にある以下の設定をお使いの環境に合わせて書き換えてください。アクセスポイントを複数記載してある場合は、上から順次接続を試みます。

```py
# WiFiアクセスポイント
WIFI_ACCESS_POINTS = [
    {"ssid": "ssid_A", "password": "pass_A"},
    {"ssid": "ssid_B", "password": "pass_B"},
    ]
```

## RSSサイトの設定

main.pyの先頭部分にある以下の設定を、閲覧したいRSSサイトに合わせて編集してください。

```py
# RSSサイト
RSS_SITES = [
    {"name": "NHK主要ニュース", "url": "https://www.nhk.or.jp/rss/news/cat0.xml"},
    {"name": "CNET Japan", "url": "http://feeds.japan.cnet.com/rss/cnet/all.rdf"},
    {"name": "GIGAZINE", "url": "https://gigazine.net/news/rss_2.0/"},
    {"name": "ITMedia 科学", "url": "https://rss.itmedia.co.jp/rss/2.0/news_technology.xml"},
    {"name": "ITMedia セキュリティ", "url": "https://rss.itmedia.co.jp/rss/2.0/news_security.xml"},
    {"name": "ITMedia 国内", "url": "https://rss.itmedia.co.jp/rss/2.0/news_domestic.xml"},
    ]
```

## 実行

電源を入れると自動的に実行されます。

## 外部ライブラリ

このプログラムは以下の外部ライブラリを使用しています。これらの外部ライブラリのライセンスに関してはそれぞれのプロジェクトをご参照ください。

- ssd1306.py  
  [micropython-ssd1306](https://github.com/stlehmann/micropython-ssd1306)
- mfontフォルダ  
  [pico_MicroPython_Multiifont](https://github.com/Tamakichi/pico_MicroPython_Multiifont)

## プログラムの留意点

RSSサイトにアクセスする際、メモリ不足でエラーになる場合があります。その場合、以下の例外処理によって端末がリセットされ、プログラムが最初から再実行されます。

```py
try:
    main()
except Exception as e:
    print(e)
    machine.reset()
```

メモリ不足になる原因はよくわからないのですが、単にHTTPS通信を連続して行うだけでもエラーになる場合があるので、Picoのハードウェア的な制約か、HTTPS通信を行うMicroPythonのライブラリに問題があるのではないかと考えています。
