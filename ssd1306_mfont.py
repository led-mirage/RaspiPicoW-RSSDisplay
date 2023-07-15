"""
SSD1306ドライバ拡張モジュール

Tamakichiさん作の下記サンプルプログラム③を引用しled-mirageが一部改変した
https://github.com/Tamakichi/pico_MicroPython_Multiifont

led-mirage (modifier). 2023. Copyright (c) Tamakichi.
"""
import time
from ssd1306 import SSD1306_I2C
from mfont import mfont


# フォントの表示
def drawFont(self, font, x, y, w, h, flg=False):
    bn = (w+7)>>3
    py = y
    for i in range(0, len(font), bn):
        px = x
        for j in range(bn):
            for k in range(8 if (j+1)*8 <=w else w % 8):
                self.pixel(px+k,py, 1 if font[i+j] & 0x80>>k else 0) 
            px+=8
        py+=1
    if flg:
        self.show()


# 改行
def newLine(self):
    line_num = int(self.height / self.mf.fs)
    line_space = int((self.height - self.mf.fs * line_num) / (line_num - 1))

    self.x=0
    if self.y+self.mf.fs*2 > self.height:
        self.scroll(0, -self.mf.fs-line_space)
        self.fill_rect(0, self.y, self.width, self.height-self.y, 0)
        self.show()
    else:
        self.y=self.y+self.mf.fs + line_space
    

# テキストの表示
def drawText(self, text, x, y, fs, wt=0):
    self.x = x
    self.y = y
    
    # フォントの設定
    self.mf = mfont(fs)
    self.mf.begin()

    # テキスト表示
    for c in text:
        if c == '\n': # 改行コードの処理
            self.newLine()
            continue
        code = ord(c) 
        font = self.mf.getFont(code)
        if self.x+self.mf.getWidth()>=self.width:
            self.newLine()
        self.drawFont(font, self.x, self.y, self.mf.getWidth(), self.mf.getHeight(), True)
        if wt:
            time.sleep_ms(wt)
        self.x+=self.mf.getWidth()
    self.mf.end()


# SSD1306_I2Cに漢字表示インスタンス・メソッドの追加
SSD1306_I2C.drawText = drawText
SSD1306_I2C.drawFont = drawFont
SSD1306_I2C.newLine  = newLine
