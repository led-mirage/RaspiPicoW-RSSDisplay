"""
RSSにアクセスして記事のタイトルと概要を表示するプログラム

Copyright (c) 2023 led-mirage
"""

from machine import Pin, I2C
import gc
import io
import network
import sys
import time
import urequests

import ssd1306_mfont
from ssd1306 import SSD1306_I2C
from mfont import mfont


# WiFiアクセスポイント
WIFI_ACCESS_POINTS = [
    {"ssid": "ssid_A", "password": "pass_A"},
    {"ssid": "ssid_B", "password": "pass_B"},
    ]

# RSSサイト
RSS_SITES = [
    {"name": "NHK主要ニュース", "url": "https://www.nhk.or.jp/rss/news/cat0.xml"},
    {"name": "CNET Japan", "url": "http://feeds.japan.cnet.com/rss/cnet/all.rdf"},
    {"name": "GIGAZINE", "url": "https://gigazine.net/news/rss_2.0/"},
    {"name": "ITMedia 科学", "url": "https://rss.itmedia.co.jp/rss/2.0/news_technology.xml"},
    {"name": "ITMedia セキュリティ", "url": "https://rss.itmedia.co.jp/rss/2.0/news_security.xml"},
    {"name": "ITMedia 国内", "url": "https://rss.itmedia.co.jp/rss/2.0/news_domestic.xml"},
    ]

# オンボードLED
led = Pin("LED", Pin.OUT)

# OLED用定数(SSD1306)
I2C_ID       = 0       # I2C ID
I2C_FREQ     = 400000  # I2C バス速度
OLED_WIDTH   = 128     # OLEDの横ドット数
OLED_HEIGHT  = 64      # OLEDの縦ドット数
OLED_ADDR    = 0x3c    # OLEDのI2Cアドレス
OLED_SCL     = 17      # OLEDのSCLピン
OLED_SDA     = 16      # OLEDのSDAピン

# OLEDディスプレイのインスタンスの生成
i2c = I2C(I2C_ID, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=I2C_FREQ)
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_ADDR)
oled.contrast(255)
oled.invert(False)

# タクトスイッチ関係
TACT_SW_PIN = 15
tact_sw = Pin(TACT_SW_PIN, Pin.IN, Pin.PULL_UP)
tact_sw_pre_time = 0 # タクトスイッチが押された時間（システム起動時からの経過時間ms）

# フォントサイズ
font_size = 16

# アプリケーションデータファイル
APP_DATA_INDEX = "app_rss_index.txt"
APP_DATA_FONTSIZE = "app_rss_fontsize.txt"


# メイン
def main():
    global font_size

    # カレントRSSインデックスを読み込む
    current_index = read_current_index(len(RSS_SITES) - 1)
    
    # フォントサイズを読み込む
    font_size = read_font_size()

    # タクトスイッチ割り込みの有効化
    tact_sw.irq(trigger=Pin.IRQ_RISING, handler=tact_sw_pushed)

    # WiFiに接続する
    oled.fill(0)
    oled.drawText("Connect to WiFi...", 0, 0, font_size, 50)
    if wifi_connect():
        oled.fill(0)
        oled.drawText("Connected!", 0, 0, font_size, 50)
    else:
        oled.fill(0)
        oled.drawText("WiFi Connect Failed!", 0, 0, font_size, 50)
        oled.drawText("Application Terminated.", 0, font_size*2, font_size, 50)
        sys.exit()
    
    # メインループ
    while True:
        for i in range(current_index, len(RSS_SITES)):
            gc.collect()
            site = RSS_SITES[i]
            write_current_index(i + 1)

            # RSSにアクセスする
            oled.fill(0)
            oled.drawText(f"Access to RSS...\n{site['name']}", 0, 0, font_size, 50)
            led.on()
            items = read_rss(site["url"])
            led.off()
            
            # タイトルを表示する
            for item in items:
                gc.collect()
                print(f"{item.title}")
                oled.fill(0)
                oled.drawText(site["name"], 0, 0, font_size, 0)
                time.sleep(1)
                oled.fill(0)
                oled.drawText("★ " + item.title, 0, 0, font_size, 50)
                time.sleep(3)
                oled.fill(0)
                oled.drawText(item.description, 0, 0, font_size, 50)
                time.sleep(5)

        current_index = 0


# WiFiに接続する
def wifi_connect():
    is_connected = False
    try_count = 0
    while is_connected == False and try_count < 10:
        for point in WIFI_ACCESS_POINTS:
            is_connected = wifi_connect_sub(point["ssid"], point["password"], 10)
            if is_connected == True:
                break
        try_count += 1
    return is_connected
            

# WiFiに接続する（サブルーチン）
def wifi_connect_sub(ssid, password, timeout):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)

    print(f"WiFi({ssid}) Connecting..", end="")
    count = 1
    while wifi.isconnected() == False:
        print(".", end="")
        time.sleep(1)
        count += 1
        if count >= timeout:
            print("Timeout")
            return False
    print("Connected!")
    return True


# RSSからアイテムのリストを取得する
def read_rss(url):
    items = []

    print(f"access to {url}")
    response = urequests.get(url)

    stream = io.StringIO(response.text)
    is_item = False
    item = None
    for line in stream:
        line_text = line.strip()
        if line_text.startswith("<item"):
            item = RssItem()
            is_item = True
        if line_text.endswith("</item>"):
            items.append(item)
            is_item = False
        if is_item and line_text.startswith("<title>"):
            item.title = line_text.replace("<title>", "").replace("</title>", "")
        if is_item and line_text.startswith("<description>"):
            item.description = strip_tags(line_text.replace("<description>", "").replace("</description>", ""))

    return items


# 簡易HTML解析・タグを除去する
def strip_tags(html_text):
    def _strip_tags(html):
        clean_text = ""
        if html.startswith("<![CDATA["):
            html = html.replace("<![CDATA[", "")
            html = html.rstrip("]>")

        taglevel = 0
        intag = False
        endtag = False
        instring = False
        for c in html:
            if c == "<":
                intag = True
                endtag = False
                continue
            elif c == ">":
                if endtag:
                    taglevel -= 1
                else:
                    taglevel += 1
                intag = False
                continue
            elif c == '"' or c == "'":
                instring = not instring
            
            if intag:
                if instring == False and c == "/":
                    endtag = True
                continue

            if taglevel == 0:
                clean_text += c
                
        clean_text = clean_text.replace("&lt;", "<").replace("&gt;", ">")
                
        return clean_text


    html_text = _strip_tags(html_text)
    html_text = _strip_tags(html_text) # 2Pass
    return html_text


# カレントのRSSサイトのインデックス番号を取得する
def read_current_index(max_index):
    return read_file(APP_DATA_INDEX, maxval=max_index)


# カレントのRSSサイトのインデックス番号を書き込む
def write_current_index(index):
    write_file(APP_DATA_INDEX, index)


# フォントサイズを取得する
def read_font_size():
    return read_file(APP_DATA_FONTSIZE, default=14)


# フォントサイズを書き込む
def write_font_size(font_size):
    write_file(APP_DATA_FONTSIZE, font_size)


# ファイルから数値を読み込む
def read_file(filename, default=0, minval=None, maxval=None):
    try:
        with open(filename, 'r') as file:
            text = file.read()
            val = int(text)
            if minval != None and val < minval:
                val = default
            if maxval != None and val > maxval:
                val = default
            return val
    except Exception as e:
        print(e)
        return default


# ファイルに数値を書き込む
def write_file(filename, val):
    with open(filename, 'w') as file:
        file.write(f"{val}")


# タクトスイッチ割込みハンドラ
# フォントサイズを変更する
def tact_sw_pushed(pin):
    global tact_sw_pre_time, font_size

    now = time.ticks_ms()
    pre_font_size = font_size
    if now - tact_sw_pre_time > 500: # 二度押し防止
        if font_size == 12:
            font_size = 14
        elif font_size == 14:
            font_size = 16
        else:
            font_size = 12
        tact_sw_pre_time = now
        write_font_size(font_size)
        
        print(f"font size: {font_size}px")
        oled.fill_rect(0, 0, 128, pre_font_size, 0)
        oled.text(f"font:{font_size}px", 2, 2)
        oled.show()
      

# RSSアイテムクラス
class RssItem:
    def __init__(self):
        self.tille = ""
        self.description = ""


try:
    main()
except Exception as e:
    print(e)
    machine.reset()
