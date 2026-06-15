from machine import I2C, SoftI2C, Pin
import time

# 1. Initialize I2C (adjust pins according to your board)
#i2c = I2C(0, scl=Pin(1), sda=Pin(2), freq=100000)
i2c = SoftI2C(scl=Pin(1), sda=Pin(2), freq=100000)

# SHT85 default I2C address
SHT85_ADDR = 0x44

# Measurement command: High repeatability, clock stretching disabled (0x2400)
MEASURE_CMD = b'\x24\x00'

def read_sht85():
    # Send measurement command
    i2c.writeto(SHT85_ADDR, MEASURE_CMD)
    
    # Wait for the measurement to complete (max ~15.5ms)
    time.sleep_ms(20)
    
    # Read 6 bytes: Temp MSB, Temp LSB, Temp CRC, Hum MSB, Hum LSB, Hum CRC
    data = i2c.readfrom(SHT85_ADDR, 6)
    
    if len(data) == 6:
        # Convert Temperature Data
        temp_raw = (data[0] << 8) | data[1]
        temperature = -45.0 + (175.0 * temp_raw / 65535.0)
        
        # Convert Humidity Data
        hum_raw = (data[3] << 8) | data[4]
        humidity = -6.0 + (125.0 * hum_raw / 65535.0)
        
        return temperature, humidity
    else:
        return None, None

# 2. Main loop
while True:
    temp, hum = read_sht85()
    if temp is not None:
        print(f"Temperature: {temp:.2f} °C | Humidity: {hum:.2f} %")
    else:
        print("Failed to read sensor")
    time.sleep(2)
