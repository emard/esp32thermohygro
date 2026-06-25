# SSD1306 display with scalable vector font
# mpremote mip install ssd1306

from time import sleep_ms
from machine import I2C,SPI,Pin
from micropython import const
from uctypes import addressof
from ssd1306 import SSD1306_I2C, SSD1306_SPI
import framebuf

def init(disp_width:int=128,disp_height:int=64,scl_pin:int=7,sda_pin:int=8,dc_pin:int=6,rst_pin:int=9,cs_pin:int=5):
  global oled,width,height
  width=disp_width
  height=disp_height
  try:
    # I2C
    #                  XIAO  ESP32S3
    #                 ┌─────────────┐
    #                 │1    USB   5V│
    #                 │2         GND│
    #                 │3        3.3V│
    #                 │4           9│
    #                 │5           8│ SDA
    #                 │6  TX       7│ SCL
    #                 │43 TXD  RX 44│
    #                 └─────────────┘
    #                    top view

    # SCL / D0    Pin     7       I2C Clock (SCL)
    # SDA / D1    Pin     8       I2C Data  (SDA)
  
    i2c = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
    oled = SSD1306_I2C(width, height, i2c)

  except:
    # SPI
    #                  XIAO  ESP32S3
    #                 ┌─────────────┐
    #                 │1    USB   5V│
    #                 │2         GND│
    #                 │3        3.3V│
    #                 │4           9│ RES Reset
    # Chip select  CS │5           8│ D1  MOSI
    # Data/Command DC │6  TX       7│ D0  SCK
    #                 │43 TXD  RX 44│
    #                 └─────────────┘
    #                    top view

    # SCL / D0    Pin     7       SPI Clock (SCK)
    # SDA / D1    Pin     8       SPI Data (MOSI)
    # RES / RST   Pin     9       Reset
    # DC          Pin     6       Data / Command
    # CS          Pin     5       Chip Select

    hspi = SPI(1)
    hspi.init(sck=Pin(scl_pin),mosi=Pin(sda_pin),miso=None)

    dc  = Pin(dc_pin)  # data/command
    rst = Pin(rst_pin) # reset
    cs  = Pin(cs_pin)  # chip select, some modules do not have a pin for this

    oled = SSD1306_SPI(width, height, hspi, dc, rst, cs)

# Initialize

  oled.poweron()
  oled.contrast(100)
  oled.invert(0)
  oled.rotate(True)
  oled.fill(0)
  oled.show()

# vector 5x7 font as associative array of polylines, delimited by 128,any
font = {
" ":bytearray([]),
".":bytearray([2,5, 2,6]),
"!":bytearray([2,0, 2,4, 128,128, 2,6, 2,6]),
"?":bytearray([0,1, 1,0, 3,0, 4,1, 4,2, 2,3, 2,4, 128,128, 2,6, 2,6]),
"|":bytearray([2,0, 2,6]),
"#":bytearray([0,2, 4,2, 128,128, 0,4, 4,4, 128,128, 1,1, 1,5, 128,128, 3,1, 3,5]),
"$":bytearray([4,1, 1,1, 0,2, 1,3, 3,3, 4,4, 3,5, 0,5, 128,128, 2,0, 2,6]),
"%":bytearray([4,1, 0,5, 128,128, 1,0, 0,1, 1,2, 2,1, 1,0, 128,128,  3,4, 2,5, 3,6, 4,5, 3,4]),
"&":bytearray([4,4, 2,6, 1,6, 0,5, 0,4, 3,1, 2,0, 1,0, 0,1, 0,2, 4,6]),
",":bytearray([2,5, 2,6, 1,7]),
":":bytearray([2,0, 2,1, 128,128, 2,5, 2,6]),
";":bytearray([2,0, 2,1, 128,128, 2,5, 2,6, 1,7]),
"+":bytearray([0,3, 4,3, 128,128, 2,1, 2,5]),
"-":bytearray([0,3, 4,3]),
"*":bytearray([0,2, 1,3, 3,3, 4,4, 128,128, 0,4, 1,3, 3,3, 4,2, 128,128, 2,1, 2,5]),
"/":bytearray([4,1, 0,5]),
"\\":bytearray([0,1, 4,5]),
"=":bytearray([0,2, 4,2, 128,128, 0,4, 4,4]),
"(":bytearray([3,0, 2,1, 2,5, 3,6]),
")":bytearray([1,0, 2,1, 2,5, 1,6]),
"[":bytearray([3,0, 2,0, 2,6, 3,6]),
"]":bytearray([1,0, 2,0, 2,6, 1,6]),
"{":bytearray([4,0, 3,0, 2,1, 2,2, 1,3, 2,4, 2,5, 3,6, 4,6, 128,128, 0,3, 1,3]),
"}":bytearray([0,0, 1,0, 2,1, 2,2, 3,3, 2,4, 2,5, 1,6, 0,6, 128,128, 3,3, 4,3]),
"_":bytearray([0,6, 4,6]),
"'":bytearray([2,0, 2,2]),
'"':bytearray([1,0, 1,2, 128,128, 3,0, 3,2]),
"^":bytearray([1,1, 2,0, 3,1]),
"~":bytearray([0,3, 1,2, 2,3, 3,2]),
"°":bytearray([1,0, 1,3, 3,3, 3,0, 1,0]),
"Δ":bytearray([2,0, 0,6, 4,6, 2,0]),
"→":bytearray([0,3, 4,3, 128,128, 2,1, 4,3, 2,5]),
">":bytearray([1,0, 4,3, 1,6]),
"<":bytearray([3,0, 0,3, 3,6]),
"0":bytearray([4,1, 3,0, 1,0, 0,1, 0,5, 1,6, 3,6, 4,5, 4,1, 0,5]),
"1":bytearray([1,1, 2,0, 2,6, 128,128, 1,6, 3,6]),
"2":bytearray([0,1, 1,0, 3,0, 4,1, 4,2, 0,6, 4,6]),
"3":bytearray([0,1, 1,0, 3,0, 4,1, 4,2, 3,3, 4,4, 4,5, 3,6, 1,6, 0,5, 128,128, 1,3, 3,3]),
"4":bytearray([3,6, 3,0, 0,3, 0,4, 4,4]),
"5":bytearray([4,0, 0,0, 0,3, 1,2, 3,2, 4,3, 4,5, 3,6, 1,6, 0,5]),
"6":bytearray([3,0, 1,0, 0,1, 0,5, 1,6, 3,6, 4,5, 4,4, 3,3, 0,3]),
"7":bytearray([0,1, 0,0, 4,0, 4,2, 1,5, 1,6]),
"8":bytearray([3,3, 4,2, 4,1, 3,0, 1,0, 0,1, 0,2, 1,3, 3,3, 4,4, 4,5, 3,6, 1,6, 0,5, 0,4, 1,3]),
"9":bytearray([1,6, 3,6, 4,5, 4,1, 3,0, 1,0, 0,1, 0,2, 1,3, 4,3]),
"@":bytearray([3,6, 1,6, 0,5, 0,1, 1,0, 3,0, 4,1, 4,4, 2,4, 2,2, 4,2]),
"A":bytearray([0,6, 0,2, 2,0, 4,2, 4,6, 128,128, 0,4, 4,4]),
"B":bytearray([3,3, 4,2, 4,1, 3,0, 0,0, 0,6, 3,6, 4,5, 4,4, 3,3, 0,3]),
"C":bytearray([4,1, 3,0, 1,0, 0,1, 0,5, 1,6, 3,6, 4,5]),
"D":bytearray([0,0, 0,6, 3,6, 4,5, 4,1, 3,0, 0,0]),
"E":bytearray([4,0, 0,0, 0,6, 4,6, 128,128, 0,3, 3,3]),
"F":bytearray([4,0, 0,0, 0,6, 128,128, 0,3, 3,3]),
"G":bytearray([4,1, 3,0, 1,0, 0,1, 0,5, 1,6, 3,6, 4,5, 4,3, 2,3]),
"H":bytearray([0,0, 0,6, 128,128, 4,0, 4,6, 128,128, 0,3, 4,3]),
"I":bytearray([2,0, 2,6, 128,128, 1,0, 3,0, 128,128, 1,6, 3,6]),
"J":bytearray([0,5, 1,6, 3,6, 4,5, 4,0]),
"K":bytearray([0,0, 0,6, 128,128, 4,0, 1,3, 0,3, 128,128, 4,6, 1,3]),
"L":bytearray([0,0, 0,6, 4,6]),
"M":bytearray([0,6, 0,0, 2,2, 4,0, 4,6]),
"N":bytearray([0,6, 0,0, 4,4, 128,128, 4,0, 4,6]),
"O":bytearray([4,1, 3,0, 1,0, 0,1, 0,5, 1,6, 3,6, 4,5, 4,1]),
"P":bytearray([0,6, 0,0, 3,0, 4,1, 4,2, 3,3, 0,3]),
"Q":bytearray([4,1, 3,0, 1,0, 0,1, 0,5, 1,6, 2,6, 4,3, 4,1, 128,128, 2,4, 4,6]),
"R":bytearray([0,6, 0,0, 3,0, 4,1, 4,2, 3,3, 0,3, 128,128, 1,3, 4,6]),
"S":bytearray([4,1, 3,0, 1,0, 0,1, 0,2, 1,3, 3,3, 4,4, 4,5, 3,6, 1,6, 0,5]),
"T":bytearray([2,0, 2,6, 128,128, 0,0, 4,0]),
"U":bytearray([0,0, 0,5, 1,6, 3,6, 4,5, 4,0]),
"V":bytearray([0,0, 0,4, 2,6, 4,4, 4,0]),
"W":bytearray([0,0, 0,6, 2,4, 4,6, 4,0]),
"X":bytearray([0,0, 0,1, 4,5, 4,6, 128,128, 0,6, 0,5, 4,1, 4,0]),
"Y":bytearray([0,0, 0,1, 2,3, 2,6, 128,128, 4,0, 4,1, 2,3]),
"Z":bytearray([0,0, 4,0, 4,1, 0,5, 0,6, 4,6]),
"Č":bytearray([4,1, 3,0, 1,0, 0,1, 0,5, 1,6, 3,6, 4,5, 128,128, 1,-2, 2,-1, 3,-2]),
"Ć":bytearray([4,1, 3,0, 1,0, 0,1, 0,5, 1,6, 3,6, 4,5, 128,128, 2,-1, 3,-2]),
"Đ":bytearray([0,0, 0,6, 3,6, 4,5, 4,1, 3,0, 0,0, 128,128, -1,3, 1,3]),
"Š":bytearray([4,1, 3,0, 1,0, 0,1, 0,2, 1,3, 3,3, 4,4, 4,5, 3,6, 1,6, 0,5, 128,128, 1,-2, 2,-1, 3,-2]),
"Ž":bytearray([0,0, 4,0, 4,1, 0,5, 0,6, 4,6, 128,128, 1,-2, 2,-1, 3,-2]),
"a":bytearray([1,2, 3,2, 4,3, 4,6, 1,6, 0,5, 1,4, 4,4]),
"b":bytearray([0,0, 0,6, 3,6, 4,5, 4,3, 3,2, 2,2, 0,4]),
"c":bytearray([4,2, 1,2, 0,3, 0,5, 1,6, 4,6]),
"d":bytearray([4,0, 4,6, 1,6, 0,5, 0,3, 1,2, 2,2, 4,3]),
"e":bytearray([0,4, 4,4, 4,3, 3,2, 1,2, 0,3, 0,5, 1,6, 3,6]),
"f":bytearray([4,1, 3,0, 2,0, 1,1, 1,6, 128,128, 0,3, 2,3]),
"g":bytearray([1,6, 3,6, 4,5, 4,2, 1,2, 0,3, 1,4, 4,4]),
"h":bytearray([0,0, 0,6, 128,128, 4,6, 4,3, 3,2, 2,2, 0,4]),
"i":bytearray([1,2, 2,2, 2,6, 128,128, 1,6, 3,6, 128,128, 2,0, 2,0]),
"j":bytearray([1,2, 2,2, 2,6, 1,7, 128,128, 2,0, 2,0]),
"k":bytearray([0,0, 0,6, 128,128, 4,2, 2,4, 4,6, 128,128, 0,4, 2,4]),
"l":bytearray([1,0, 2,0, 2,6, 128,128, 1,6, 3,6]),
"m":bytearray([0,6, 0,2, 3,2, 4,3, 4,6, 128,128, 2,2, 2,6]),
"n":bytearray([0,6, 0,2, 3,2, 4,3, 4,6]),
"o":bytearray([4,3, 3,2, 1,2, 0,3, 0,5, 1,6, 3,6, 4,5, 4,3]),
"p":bytearray([0,7, 0,2, 3,2, 4,3, 4,4, 3,5, 0,5]),
"q":bytearray([4,7, 4,2, 1,2, 0,3, 0,4, 1,5, 4,5]),
"r":bytearray([0,6, 0,2, 128,128, 0,4, 2,2, 4,2]),
"s":bytearray([4,2, 1,2, 0,3, 1,4, 3,4, 4,5, 3,6, 0,6]),
"t":bytearray([2,0, 2,5, 3,6, 4,6, 128,128, 1,2, 3,2]),
"u":bytearray([0,2, 0,5, 1,6, 4,6, 4,2]),
"v":bytearray([0,2, 0,4, 2,6, 4,4, 4,2]),
"w":bytearray([0,2, 0,5, 1,6, 4,6, 4,2, 128,128, 2,2, 2,6]),
"x":bytearray([0,2, 4,6, 128,128, 0,6, 4,2]),
"y":bytearray([0,2, 0,4, 1,5, 4,5, 128,128, 4,2, 4,6, 3,7, 1,7]),
"z":bytearray([0,2, 4,2, 0,6, 4,6]),
"č":bytearray([4,2, 1,2, 0,3, 0,5, 1,6, 4,6, 128,128, 1,0, 2,1, 3,0]),
"ć":bytearray([4,2, 1,2, 0,3, 0,5, 1,6, 4,6, 128,128, 2,1, 3,0]),
"đ":bytearray([4,0, 4,6, 1,6, 0,5, 0,3, 1,2, 2,2, 4,3, 128,128, 3,1, 5,1]),
"š":bytearray([4,2, 1,2, 0,3, 1,4, 3,4, 4,5, 3,6, 0,6, 128,128, 1,0, 2,1, 3,0]),
"ž":bytearray([0,2, 4,2, 0,6, 4,6, 128,128, 1,0, 2,1, 3,0]),
}

# x,y  = offset
# xscale, yscale = 256 default for 5x7 font
# line = bytearray([x0,y0, x1,y1, ... xn,yn]); 128,any=delimiter
# buf  = bytearray([x1,y1,x2,y2,color])
@micropython.viper
def polyline_fast(x:int, y:int, xscale:int, yscale:int, line, buf):
  if x >= int(width) or y >= int(height):
    return
  p = ptr8(addressof(line))
  b = ptr8(addressof(buf))
  n = 0
  for i in range(int(len(line))>>1):
    xp = p[2*i]
    if xp == 128: # discontinue polyline
      n = 0 # start new polyline
    else:
      b[  2*(i&1)] = ((     xp *xscale)>>8)+x
      b[1+2*(i&1)] = ((p[1+2*i]*yscale)>>8)+y
      if n:
        oled.line(b[0],b[1],b[2],b[3],b[4])
      else:
        n = 1

# x,y = coordinate upper left corner of the first char
# xscale, yscale = 256 for default size, 128 for half size, 512 for double size
# text = string
# color = bytearray([r,g,b])
# spacing = between chars
def text(text, x=0, y=0, color=1, spacing=6, xscale=256, yscale=256):
  buf = bytearray([0,0,0,0,color])
  x0 = x
  for char in text:
    polyline_fast(x0,y,xscale,yscale,font[char],buf)
    x0 += spacing

# sensor = 1 or 2
def thdisp(sensor:int, model:str, t:float, rh:float, serial:int):
  x0=((sensor-1) & 1)*64
  xunit=47
  #boldtext=((0,0)) # thin text, not bold
  boldtext=((0,0),(0,1),(1,1),(1,0)) # bold text
  oled.fill_rect(x0,0,x0+64,64,0)
  text("%-5s %d" % (model,sensor,), x0, 0, 1)
  if t>-99 and t<200:
    for bold in boldtext: # for bold text
      if t>0 and t<100:
        text("%4.1f" % (t,), x0+bold[0], 16+bold[1], 1, 12, 512, 512)
      else:
        text("%4.0f" % (t,), x0+bold[0], 16+bold[1], 1, 12, 512, 512)
      if rh>0 and rh<100:
        text("%4.1f" % (rh,), x0+bold[0], 32+bold[1], 1, 12, 512, 512)
      else:
        text("%4.0f" % (rh,), x0+bold[0], 32+bold[1], 1, 12, 512, 512)
    text("°C", x0+xunit, 16,1)
    text("%", x0+xunit, 32, 1)
    if serial:
      text("%08X" % (serial,), x0, 56, 1)
  oled.show()

def demo():
  text("1234ABCD",1,32,1,12,512,512)
  text("ΔČĆĐŠŽčćđšž",0,16,1)
  oled.show()

#thdisp(1,10,20)
#thdisp(2,15,22)
#demo()
