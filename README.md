# Arduino Thermo-Hygrometer for Heltec kit

# Controller

    HELTEC ESP32 LoRa KIT pinout top view

             GND o -- USB -- o GND
              5V o RST   PRG o  5v
             3V3 o           o 3v3
             GND o           o  36
              RX o           o  37
              TX o           o  38
             RST o  -------  o  39
    Button     0 o |       | o  34
         SCL1 22 o |       | o  35 
    LoRa MISO 19 o |       | o  32
         SCL2 23 o |       | o  33
    LoRa CS   18 o |       | o  25   LED
    LoRa SCK   5 o |       | o  26   LoRa IRQ
    OLED SCL  15 o |       | o  27   LoRa MOSI
               2 o |       | o  14   LoRa RST
    OLED SDA   4 o |       | o  12
              17 o  -------  o  13   SDA2
    OLED RST  16 o ----O---- o  21   SDA1

# Sensor Sensirion SHT75

[SHT75 datasheet](https://www.mouser.com/datasheet/2/682/Sensirion_Humidity_SHT7x_Datasheet_V5-469726.pdf)

       ----
      |HLM |
      | 75 |
       -  -
        ||
       -  -
      |    |
       ||||
       1234

    pin signal
    --- ---
     1  SCK
     2  VDD
     3  GND
     4  DATA

# Sensor in sonbest-slht14-5-RJ45 assembly

[slht14-5-RJ45 datasheet](http://www.sonbest.com/uploads/soft/151029/2-151029160H7.pdf)

        ----
     ---    ---
    |          |
    | 87654321 |
     ----------

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

# Sensor in the Probus assembly

    Probus sensor DIN 8-pin
    Inside chip SHT75
    Text written on the chip
     ---
    |HLM|
    |75 |
     --- 
    
    looking at the pins DIN-8
    
    
                U
              6   7
             1  8  3
              4   5
                2
    
    pin signal
    --- -----
     4  SCK
     8  VDD
     1  GND
     6  DATA

# RJ45 adapter for Probus DIN 8-pin

    RJ45 crimped on cable, looking at the pins
    
        |c |
        |a |
        |b |
        |l |
        |e |
     ---    ---   
    |          |
    |          |
    | |||||||| |
    | 87654321 |
     ----------
    
    RJ45                         DIN-8
    pin  color          signal   pin
    ---  ------------   ------   -----
     1   green-white
     2   green
     3   orange-white   GND      1
     4   blue           DATA     6
     5   blue-white     SCK      4
     6   orange         VDD      8
     7   brown-white
     8   brown                   shield
    
    Probus sensor DIN 8-pin on cable, looking at the pins
    
                     U
    blue           6   7
    orange-white  1  8  3
    blue-white     4   5
                     2

