from sht75 import SHT75
from sht85 import SHT85
import ssd1306txt

# XIAO ESP32S3 SHT75/SHT85 SSD1306 I2C/SPI

# looking at plastic package
# back side is golden
#      ┌────┐
#      │HLM │
#      │ 75 │
#      └─┐┌─┘
#        ││
#      ┌─┘└─┐
#      │    │
#      └────┘
#       ││││
#       1234

#    pin signal
#    --- ---
#     1  SCK
#     2  VDD
#     3  GND
#     4  DATA

# Sensor in sonbest-slht14-5-RJ45 assembly

#     RJ45 socket
#   looking at hole
#   pins are down
#       ┌────┐
#    ┌──┘    └──┐
#    │          │
#    │ 87654321 │
#    └──────────┘

#    RJ45 crimped on cable
#    looking at the pins
#        │c │
#        │a │
#        │b │
#        │l │
#        │e │
#    ┌──────────┐
#    │   │  │   │
#    │          │
#    │          │
#    │          │
#    │ ││││││││ │
#    │ 87654321 │
#    └──────────┘

#    pin  color          signal
#    ---  ------------   ------
#     1   orange-white
#     2   orange
#     3   green-white    GND
#     4   blue           SDA
#     5   blue-white     SCK
#     6   green          3V3
#     7   brown-white
#     8   brown

#                     XIAO  ESP32S3
#                    ┌─────────────┐
#    SHT75 2    SCK2 │1    USB   5V│
#    SHT75 2    SDA2 │2         GND│
#    SHT75 1    SCK1 │3        3.3V│
#    SHT75 1    SDA1 │4           9│ RES Reset
#    Chip select  CS │5           8│ D1  SDA/MOSI
#    Data/Command DC │6  TX       7│ D0  SCL/SCK
#                    │43 TXD  RX 44│
#                    └─────────────┘
#                       top view

sensor1_scl_pin=const(3)
sensor1_sda_pin=const(4)
sensor2_scl_pin=const(1)
sensor2_sda_pin=const(2)

#      SSD1306 OLED I2C DISPLAY
#    ┌──────────────────────────┐
#    │     GND VCC SCL SDA      │
#    │┌────────────────────────┐│
#    ││                        ││
#    ││          0.96"         ││
#    ││         128x64         ││
#    ││                        ││
#    ││                        ││
#    │└────────────────────────┘│
#    └──────────────────────────┘
#               top view

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

#      SSD1306 OLED SPI DISPLAY
#    ┌──────────────────────────┐
#    │GND VCC D0  D1  RES DC  CS│
#    │┌────────────────────────┐│
#    ││                        ││
#    ││          0.96"         ││
#    ││         128x64         ││
#    ││                        ││
#    ││                        ││
#    │└────────────────────────┘│
#    └──────────────────────────┘
#               top view

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

display_width=const(128)
display_height=const(64)
display_scl_pin=const(7)
display_sda_pin=const(8)
display_rst_pin=const(9)
display_dc_pin=const(6)
display_cs_pin=const(5)

ssd1306txt.init(disp_width=display_width,disp_height=display_height,
scl_pin=display_scl_pin,sda_pin=display_sda_pin,
rst_pin=display_rst_pin,dc_pin=display_dc_pin,cs_pin=display_cs_pin)

t1=-99.9
rh1=-99.9
model1=""
t2=-99.9
rh2=-99.9
model2=""
while True:
  if t1<-99:
    model1="SHT85"
    sensor1=SHT85(sck_pin=sensor1_scl_pin, data_pin=sensor1_sda_pin)
    if sensor1.detect()==False:
      model1="SHT75"
      sensor1=SHT75(sck_pin=sensor1_scl_pin, data_pin=sensor1_sda_pin, chip_v=4)
  t1,rh1,serial1=sensor1.read_temp_humidity()    
  if t1<-99:
    model1=""
  ssd1306txt.thdisp(1,model1,t1,rh1,serial1)
  if t2<-99:
    model2="SHT85"
    sensor2=SHT85(sck_pin=sensor2_scl_pin, data_pin=sensor2_sda_pin)
    if sensor2.detect()==False:
      model2="SHT75"
      sensor2=SHT75(sck_pin=sensor2_scl_pin, data_pin=sensor2_sda_pin, chip_v=4)
  t2,rh2,serial2=sensor2.read_temp_humidity()
  if t2<-99:
    model2=""
  ssd1306txt.thdisp(2,model2,t2,rh2,serial2)
  print("T1=%5.2f C RH1=%5.2f %% T2=%5.2f C RH2=%5.2f %% " % (t1,rh1,t2,rh2))
