from machine import Pin,SoftI2C
from time import sleep_ms

# SHT85 default I2C address
SHT85_ADDR = const(0x44)

# Measurement command: High repeatability, clock stretching disabled (0x2400)
MEASURE_CMD = b'\x24\x00'

class SHT85:
  def __init__(self, sck_pin:int, data_pin:int):
    self.i2c=SoftI2C(scl=Pin(sck_pin), sda=Pin(data_pin), freq=100000)

  def detect(self)->bool:
    if SHT85_ADDR in self.i2c.scan():
      return True
    return False

  def read_temp_humidity(self)->Tuple(float,float):
    # Send measurement command
    try:
      self.i2c.writeto(SHT85_ADDR, MEASURE_CMD)
    except: # ENODEV
      return -99.9, -99.9
    
    # Wait for the measurement to complete (max ~15.5ms)
    sleep_ms(20)
    
    # Read 6 bytes: Temp MSB, Temp LSB, Temp CRC, Hum MSB, Hum LSB, Hum CRC
    data = self.i2c.readfrom(SHT85_ADDR, 6)
    
    if len(data) == 6:
        # Convert Temperature Data
        temp_raw = (data[0] << 8) | data[1]
        temperature = 175 * temp_raw / 65535 - 45
        
        # Convert Humidity Data
        hum_raw = (data[3] << 8) | data[4]
        humidity = 100 * hum_raw / 65535
        
        return temperature, humidity
    else:
        return -99.9, -99.9
