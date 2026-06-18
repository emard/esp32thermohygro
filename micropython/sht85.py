from machine import Pin,SoftI2C
from time import sleep_ms
from shtcrctab import crctable

# SHT85 default I2C address
SHT85_ADDR = const(0x44)

# Measurement command: High repeatability, clock stretching disabled (0x2400)
MEASURE_CMD = b'\x24\x00'
READ_SERIAL_CMD = b'\x36\x82'

class SHT85:
  def __init__(self, sck_pin:int, data_pin:int):
    self.i2c=SoftI2C(scl=Pin(sck_pin), sda=Pin(data_pin), freq=100000)

  def detect(self)->bool:
    if SHT85_ADDR in self.i2c.scan():
      return True
    return False

  def crc_calc(self, msb:int, lsb:int)->int:
    crc = 0xFF
    crc = crctable[crc ^ msb]
    crc = crctable[crc ^ lsb]
    return crc
  
  def read_serial_no(self)->int:
    try:
      self.i2c.writeto(SHT85_ADDR, READ_SERIAL_CMD)
    except:
      return 0
    sleep_ms(1)
    try:
      data = self.i2c.readfrom(SHT85_ADDR, 6)
    except:
      return 0
    if len(data) == 6:
      if self.crc_calc(data[0],data[1]) == data[2] and self.crc_calc(data[3],data[4]) == data[5]:
        return data[0]<<24 | data[1]<<16 | data[3]<<8 | data[4]
      else:
        return 0
    else:
      return 0

  # T[°C], RH[%], serial_no (32-bit integer)
  def read_temp_humidity(self)->Tuple(float,float,int):
    serial_no = self.read_serial_no()

    # Send measurement command
    try:
      self.i2c.writeto(SHT85_ADDR, MEASURE_CMD)
    except: # ENODEV
      return -99.9, -99.9, serial_no

    # Wait for the measurement to complete (max ~15.5ms)
    sleep_ms(20)

    # Read 6 bytes: Temp MSB, Temp LSB, Temp CRC, Hum MSB, Hum LSB, Hum CRC
    try:
      data = self.i2c.readfrom(SHT85_ADDR, 6)
    except:
      return -99.9, -99.9, serial_no

    if len(data) == 6:
        # Convert Temperature Data
        if self.crc_calc(data[0],data[1]) == data[2]:
          temp_raw = (data[0] << 8) | data[1]
          temperature = 175 * temp_raw / 65535 - 45
        else:
          temperature = -99.9

        # Convert Humidity Data
        if self.crc_calc(data[3],data[4]) == data[5]:
          hum_raw = (data[3] << 8) | data[4]
          humidity = 100 * hum_raw / 65535
        else:
          humidity = -99.9

        return temperature, humidity, serial_no
    else:
        return -99.9, -99.9, serial_no
