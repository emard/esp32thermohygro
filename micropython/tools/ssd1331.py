# Micropython ESP32S3 SSD1331 display driver

#        XIAO  ESP32S3
#           ┌─────┐
#       ┌───┘ USB └───┐
#       │1          5V│
#    CS │2         GND│ GND
#    DC │3        3.3V│ 3.3V
#   RES │4           9│
#   SDA │5           8│
#   SCL │6           7│
#       │43 TX   RX 44│
#       └─────────────┘
#           top view

from time import sleep_ms
from machine import SPI,Pin
from micropython import const
from uctypes import addressof
import framebuf, pinout

# XIAO MINI
#gpio_csn = const(2)
#gpio_dc = const(3)
#gpio_resn = const(4)
#gpio_sda = const(5)
#gpio_sck = const(6)

# DEVKIT
#gpio_csn = const(38)
#gpio_dc = const(39)
#gpio_resn = const(40)
#gpio_sda = const(41)
#gpio_sck = const(42)

dc=Pin(pinout.disp_dc,Pin.OUT)
resn=Pin(pinout.disp_resn,Pin.OUT)
csn=Pin(pinout.disp_csn,Pin.OUT)
oled_spi=SPI(2, baudrate=6600000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=pinout.disp_sck, mosi=pinout.disp_sda, miso=None)

C_OLED_NOP1 = const(0xBC)
C_OLED_NOP2 = const(0xBD) # delay nop
C_OLED_NOP3 = const(0xE3)
C_OLED_SET_DISPLAY_OFF = const(0xAE) # 0b10101110
C_OLED_SET_REMAP_COLOR = const(0xA0)
C_OLED_REMAP_COLOR_VALUE = const(0x60) # 0b01100000 # A[6]=0:RGB332, A[6]=1:RGB565; A[0]=0:left-to-right A[1]=top-to-bottom
C_OLED_SET_DISPLAY_START_LINE = const(0xA1) # 0
C_OLED_SET_DISPLAY_OFFSET = const(0xA2) # 0
C_OLED_SET_DISPLAY_MODE_NORMAL = const(0xA4)
C_OLED_SET_MULTIPLEX_RATIO = const(0xA8)
C_OLED_SET_MASTER_CONFIGURATION = const(0xAD)
C_OLED_SET_POWER_SAVE_MODE = const(0xB0)
C_OLED_SET_PHASE_1_AND_2_PERIOD_ADJUSTMENT = const(0xB1)
C_OLED_SET_DISPLAY_CLOCK_DIVIDER = const(0xF0)
C_OLED_SET_PRECHARGE_A = const(0x8A)
C_OLED_SET_PRECHARGE_B = const(0x8B)
C_OLED_SET_PRECHARGE_C = const(0x8C)
C_OLED_SET_PRECHARGE_LEVEL = const(0xBB)
C_OLED_SET_VCOMH = const(0xBE)
C_OLED_SET_MASTER_CURRENT_CONTROL = const(0x87)
C_OLED_SET_CONTRAST_COLOR_A = const(0x81)
C_OLED_SET_CONTRAST_COLOR_B = const(0x82)
C_OLED_SET_CONTRAST_COLOR_C = const(0x83)
C_OLED_SET_COLUMN_ADDRESS = const(0x15)
C_OLED_SET_ROW_ADDRESS = const(0x75)
C_OLED_SET_DISPLAY_ON = const(0xAF)
C_OLED_DRAW_LINE = const(0x21) # x0,y0,x1,y1,color_c,color_b,color_a
C_OLED_DRAW_RECTANGLE = const(0x22) # x0,y0,x1,y1,outline_c,outline_b,outline_a,fill_c,fill_b,fill_a
C_OLED_FILL_ENABLE = const(0x26) # a[0]=1 enable rectangle fill, a[4]=1 enable reverse copy
C_OLED_COPY = const(0x23) # x0,y0,x1,y1,x2,y2 copy 0-1 to 2
C_OLED_CLEAR_WINDOW = const(0x25) # x0,y0,x1,y1

oled_init_sequence = bytearray([
C_OLED_NOP1, # 0, 10111100
C_OLED_SET_DISPLAY_OFF, # 1, 0b10101110
C_OLED_SET_REMAP_COLOR, C_OLED_REMAP_COLOR_VALUE, # 2
C_OLED_SET_DISPLAY_START_LINE, 0x00, # 4
C_OLED_SET_DISPLAY_OFFSET, 0x00, # 6
C_OLED_SET_DISPLAY_MODE_NORMAL, # 8
C_OLED_SET_MULTIPLEX_RATIO, 0x3F, # 0b00111111, # 9, 15-16
C_OLED_SET_MASTER_CONFIGURATION, 0x8E, # 0b10001110, # 11, a[0]=0 Select external Vcc supply, a[0]=1 Reserved(reset)
C_OLED_SET_POWER_SAVE_MODE, 0x00, # 13, 0-no power save, 0x1A-power save
C_OLED_SET_PHASE_1_AND_2_PERIOD_ADJUSTMENT, 0x74, # 15
C_OLED_SET_DISPLAY_CLOCK_DIVIDER, 0xF0, # 17
C_OLED_SET_PRECHARGE_A, 0x64, # 19
C_OLED_SET_PRECHARGE_B, 0x78, # 21
C_OLED_SET_PRECHARGE_C, 0x64, # 23
C_OLED_SET_PRECHARGE_LEVEL, 0x31, # 25
C_OLED_SET_CONTRAST_COLOR_A, 0xFF, # 27, 255
C_OLED_SET_CONTRAST_COLOR_B, 0xFF, # 29, 255
C_OLED_SET_CONTRAST_COLOR_C, 0xFF, # 31, 255
C_OLED_SET_VCOMH, 0x3E,
C_OLED_SET_MASTER_CURRENT_CONTROL, 0x06,
C_OLED_SET_COLUMN_ADDRESS, 0x00, 0x5F, # 33, 96
C_OLED_SET_ROW_ADDRESS, 0x00, 0x3F, # 36, 63
C_OLED_SET_DISPLAY_ON, # 39
C_OLED_NOP1, # 40 -- during debugging sent as data
]) # end bytearray

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

width = const(96)
height = const(64)
fb = framebuf.FrameBuffer(bytearray(width * height * 2), width, height, framebuf.RGB565)

def fb_show():
  dc.value(0) # command
  oled_spi.write(bytearray([
    C_OLED_SET_COLUMN_ADDRESS, 0, width-1, # 96
    C_OLED_SET_ROW_ADDRESS,    0, height-1, # 64
  ]))
  dc.value(1) # data
  oled_spi.write(fb)

def oled_horizontal_line(y, color):
  line([0,y,width-1,y],color)

# line = bytearray([x0,y0,x1,y1])
# color = bytearray([r,g,b])
def line(line, color):
  dc.value(0) # command
  oled_spi.write(bytearray([C_OLED_DRAW_LINE]) + bytearray(line) + bytearray(color))

def scroll_up(n):
  dc.value(0) # command
  oled_spi.write(bytearray([C_OLED_COPY]) + bytearray([0,n, width-1, height-1, 0,0]))

# x,y  = offset
# xscale, yscale = 256 default for 5x7 font
# line = bytearray([x0,y0, x1,y1, ... xn,yn]); 128,any=delimiter
# buf  = bytearray([C_OLED_DRAW_LINE,0,0,0,0,color[0],color[1],color[2]])
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
      b[1+2*(i&1)] = ((     xp *xscale)>>8)+x
      b[2+2*(i&1)] = ((p[1+2*i]*yscale)>>8)+y
      if n:
        oled_spi.write(buf)
      else:
        n = 1

# x,y = coordinate upper left corner of the first char
# xscale, yscale = 256 for default size, 128 for half size, 512 for double size
# text = string
# color = bytearray([r,g,b])
# spacing = between chars
def text(text, x=0, y=0, color=b"\xFF\xFF\xFF", spacing=6, xscale=256, yscale=256):
  dc.value(0) # command
  buf = bytearray([C_OLED_DRAW_LINE,0,0,0,0,color[0],color[1],color[2]])
  x0 = x
  for char in text:
    polyline_fast(x0,y,xscale,yscale,font[char],buf)
    x0 += spacing

# line = bytearray([x0,y0,x1,y1])
# outline,inside = bytearray([r,g,b])
def box(box, outline, inside):
  dc.value(0) # command
  oled_spi.write(bytearray([C_OLED_FILL_ENABLE, 1]))
  oled_spi.write(bytearray([C_OLED_DRAW_RECTANGLE]) + bytearray(box) + bytearray(outline) + bytearray(inside))

# fills box with 0 (black)
def box_black(box):
  dc.value(0) # command
  oled_spi.write(bytearray([C_OLED_CLEAR_WINDOW]) + bytearray(box))

def oled_color_stripes(y):
  y = y & 63
  oled_horizontal_line((y+ 0) & 63, [255,255,255]) # white
  oled_horizontal_line((y+16) & 63, [  0,  0,255]) # blue
  oled_horizontal_line((y+32) & 63, [  0,255,  0]) # green
  oled_horizontal_line((y+48) & 63, [255,  0,  0]) # red

def oled_run_stripes(n):
  for i in range(n):
    oled_color_stripes(i)
    sleep_ms(5)

def demo():
  print("4 horizontal stripes (RGBW) scrolling down")
  oled_run_stripes(128)
  # scroll some text
  black = bytearray([0,0,0])
  white = bytearray([255,255,255])
  yellow = bytearray([255,255,0])
  print("scroll line 0..99")
  for i in range(100):
    scroll_up(8)
    sleep_ms(1) # wait for scroll to finish
    box_black(bytearray([0,56,95,63])) # text background
    text("SCROLL %d" % i,0,56,white) # text foreground
  print("print('MicroPython!'), raster font 8x8, underlined")
  fb.fill(0)
  fb.text('MicroPython!', 0, 0, 0xffff)
  fb.hline(0, 10, 96, 0xffff)
  fb_show()
  print("blue box with red outline")
  box(bytearray([0,30,95,63]),bytearray([170,0,0]),bytearray([0,0,170]))
  print("print('1234ABCD'), vector font 12x16 (10x14)")
  text("1234ABCD",1,32,white,12,512,512)
  print("print('CČĆĐŠŽčćđšž'), vector font 6x8 (5x7)")
  text("ΔČĆĐŠŽčćđšž",0,16,yellow)

csn.value(0) # enable OLED
dc.value(0) # commands
resn.value(0)
sleep_ms(5)
resn.value(1)
sleep_ms(20)
oled_spi.write(oled_init_sequence)
box([0,0,width-1,height-1],[0,64,128],[0,64,128])
#demo()
