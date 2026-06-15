# Pinout

                     XIAO  ESP32S3
                    ┌─────────────┐
    SHT75 2    SCK2 │1    USB   5V│
    SHT75 2    SDA2 │2         GND│
    SHT75 1    SCK1 │3        3.3V│
    SHT75 1    SDA1 │4           9│ RES Reset
    Chip select  CS │5           8│ D1  MOSI
    Data/Command DC │6  TX       7│ D0  SCK
                    │43 TXD  RX 44│
                    └─────────────┘
                       top view

        SSD1306 OLED DISPLAY
    ┌──────────────────────────┐
    │GND VCC D0  D1  RES DC  CS│ 
    │┌────────────────────────┐│ 
    ││                        ││ 
    ││                        ││ 
    ││                        ││ 
    ││                        ││ 
    ││                        ││ 
    │└────────────────────────┘│ 
    └──────────────────────────┘
               top view

    SCL / D0    Pin     7       SPI Clock (SCK)
    SDA / D1    Pin     8       SPI Data (MOSI)
    RES / RST   Pin     9       Reset
    DC          Pin     6       Data / Command
    CS          Pin     5       Chip Select
