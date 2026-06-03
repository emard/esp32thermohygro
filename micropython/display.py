# upip.install('micropython-ssd1306')

# OLED: SSD1306 128x64

from machine import SPI,Pin
from ssd1306 import SSD1306_I2C, SSD1306_SPI
import time

if 0:
  oledrst = Pin(16)

  oledrst.value(0)
  time.sleep(0.1)
  oledrst.value(1)
  time.sleep(0.1)

  i2c = machine.I2C(sda=Pin(4), scl=Pin(15))
  i2c.scan()

  # This shows us that there is a device on address 60 which is 3C in Hex.
  # That is where our display is supposed to live.
  # Now we create an object for our OLED display.

  oled = SSD1306_I2C(128, 64, i2c)

if 1:
  #                  XIAO  ESP32S3
  #                 ┌─────────────┐
  #            SDA2 │1    USB   5V│
  #            SCK2 │2         GND│
  #            SDA1 │3        3.3V│
  #            SCK1 │4           9│ RES Reset
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
  hspi.init(sck=Pin(7),mosi=Pin(8),miso=None)

  dc = Pin(6)    # data/command
  rst = Pin(9)   # reset
  cs = Pin(5)   # chip select, some modules do not have a pin for this

  oled = SSD1306_SPI(128, 64, hspi, dc, rst, cs)

# Initialize

oled.poweron()
oled.contrast(100)
oled.invert(0)
oled.rotate(True)
oled.fill(0)

# This is it. Now we can use our OLED display:

oled.fill(1)
oled.show()

# This fills the whole display with white pixels. To clear the display do:

oled.fill(0)
oled.show()

# Now we can also write some text:

#oled.text('Hello', 0, 0)
#oled.text('World', 0, 10)
#oled.show()

# Diagonal Line: line(x1, y1, x2, y2, color)
# Horizontal Line: hline(x, y, width, color)
# Vertical Line: vline(x, y, height, color)

#oled.line(2,5, 20,15, 1)
#oled.hline(7,10,15,1)
#oled.vline(23,2,10,1)
#oled.show()

# rectangle

#oled.fill_rect(10, 10, 16, 14, 1)

# power off and power on for display saver

oled.poweroff()
time.sleep(1)
oled.poweron()

# another demo

def demo():
  oled.rect(0, 0, 128, 64, 1)
  oled.fill_rect(2, 2, 30, 30, 1)
  oled.fill_rect(4, 4, 26, 26, 0)
  oled.vline(9, 8, 22, 1)
  oled.vline(16, 2, 22, 1)
  oled.vline(23, 8, 22, 1)
  oled.fill_rect(27, 24, 1, 2, 1)
  oled.text('MicroPython', 38, 2, 1)
  oled.text('SSD1306', 38, 14, 1)
  oled.text('OLED 128x64', 38, 26, 1)
  oled.text('1.3 Inch', 18, 50, 1)
  oled.show()

def display_t_rh(t1:float,rh1:float,t2:float,rh2:float):
  oled.fill_rect(0,0,128,64,0)
  oled.text("C", 50, 14, 1)
  oled.text("%", 50, 26, 1)
  if t1>-10 and t1<100:
    oled.text("%5.2f" % (t1,), 0, 14, 1)
    oled.text("%5.2f" % (rh1,), 0, 26, 1)
  if t2>-10 and t2<100:
    oled.text("%5.2f" % (t2,), 64, 14, 1)
    oled.text("%5.2f" % (rh2,), 64, 26, 1)
  oled.show()

# demo()
# display_t_rh(20.2,34.4,30.3,55.5)
  