# Pinout

XIAO ESP32S3 SHT75/SHT85 SSD1306 I2C/SPI

looking at plastic package
back side is golden
     ┌────┐
     │HLM │
     │ 75 │
     └─┐┌─┘
       ││
     ┌─┘└─┐
     │    │
     └────┘
      ││││
      1234

    pin signal
    --- ---
     1  SCK
     2  VDD
     3  GND
     4  DATA

Sensor in sonbest-slht14-5-RJ45 assembly

    RJ45 socket
    looking at hole
    pins are down
       ┌────┐
    ┌──┘    └──┐
    │          │
    │ 87654321 │
    └──────────┘

    RJ45 crimped on cable
    looking at the pins
        │c │
        │a │
        │b │
        │l │
        │e │
    ┌──────────┐
    │   │  │   │
    │          │
    │          │
    │          │
    │ ││││││││ │
    │ 87654321 │
    └──────────┘

    pin  color          signal
    ---  ------------   ------
     1   orange-white
     2   orange
     3   green-white    GND
     4   blue           SDA
     5   blue-white     SCK
     6   green          3V3
     7   brown-white
     8   brown

                     XIAO  ESP32S3
                    ┌─────────────┐
    SHT75 2    SCK2 │1    USB   5V│
    SHT75 2    SDA2 │2         GND│
    SHT75 1    SCK1 │3        3.3V│
    SHT75 1    SDA1 │4           9│ RES Reset
    Chip select  CS │5           8│ D1  SDA/MOSI
    Data/Command DC │6  TX       7│ D0  SCL/SCK
                    │43 TXD  RX 44│
                    └─────────────┘
                       top view

      SSD1306 OLED I2C DISPLAY
    ┌──────────────────────────┐
    │     GND VCC SCL SDA      │
    │┌────────────────────────┐│
    ││                        ││
    ││          0.96"         ││
    ││         128x64         ││
    ││                        ││
    ││                        ││
    │└────────────────────────┘│
    └──────────────────────────┘
               top view

I2C
                 XIAO  ESP32S3
                ┌─────────────┐
                │1    USB   5V│
                │2         GND│
                │3        3.3V│
                │4           9│
                │5           8│ SDA
                │6  TX       7│ SCL
                │43 TXD  RX 44│
                └─────────────┘
                   top view

    SCL / D0    Pin     7       I2C Clock (SCL)
    SDA / D1    Pin     8       I2C Data  (SDA)

      SSD1306 OLED SPI DISPLAY
    ┌──────────────────────────┐
    │GND VCC D0  D1  RES DC  CS│
    │┌────────────────────────┐│
    ││                        ││
    ││          0.96"         ││
    ││         128x64         ││
    ││                        ││
    ││                        ││
    │└────────────────────────┘│
    └──────────────────────────┘
               top view

SPI

                     XIAO  ESP32S3
                    ┌─────────────┐
                    │1    USB   5V│
                    │2         GND│
                    │3        3.3V│
                    │4           9│ RES Reset
    Chip select  CS │5           8│ D1  MOSI
    Data/Command DC │6  TX       7│ D0  SCK
                    │43 TXD  RX 44│
                    └─────────────┘
                       top view

    SCL / D0    Pin     7       SPI Clock (SCK)
    SDA / D1    Pin     8       SPI Data (MOSI)
    RES / RST   Pin     9       Reset
    DC          Pin     6       Data / Command
    CS          Pin     5       Chip Select
