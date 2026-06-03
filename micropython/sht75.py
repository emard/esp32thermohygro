from machine import Pin
#from time import sleep_us

import machine
import time

class SHT75:
    def __init__(self, sck_pin, data_pin):
        self.sck = machine.Pin(sck_pin, machine.Pin.OUT)
        self.data = machine.Pin(data_pin, machine.Pin.OUT)
        self.data.init(machine.Pin.OPEN_DRAIN, machine.Pin.PULL_UP)
        self.sck.value(0)

    def _send_command(self, cmd):
        self.data.init(Pin.OUT)
        # Transmission Start sequence
        self.data.value(1)
        self.sck.value(0)
        self.sck.value(1)
        self.data.value(0)
        self.sck.value(0)
        self.sck.value(1)
        self.data.value(1)
        self.sck.value(0)
        
        # Send command byte
        for i in range(8):
            self.data.value((cmd >> (7 - i)) & 1)
            self.sck.value(1)
            self.sck.value(0)
            
        # Verify Acknowledge
        self.data.init(Pin.IN)
        self.sck.value(1)
        ack = self.data.value()
        self.sck.value(0)
        if ack != 0:
            print("Sensor did not acknowledge command")
            
    def _wait_for_conversion(self):
        self.data.init(Pin.IN)
        timeout = 0
        while self.data.value() != 0:
            time.sleep_ms(10)
            timeout += 10
            if timeout > 300:
                print("Sensor conversion timeout")
                break

    def _read_byte(self, ack):
        byte = 0
        self.data.init(Pin.IN)
        for i in range(8):
            self.sck.value(1)
            byte = (byte << 1) | self.data.value()
            self.sck.value(0)
            
        # Send Acknowledge
        self.data.init(Pin.OUT)
        self.data.value(ack)
        self.sck.value(1)
        self.sck.value(0)
        self.data.init(Pin.IN)
        return byte

    def read_temp_humidity(self):
        # Read Temperature
        # 0x03 is the command for reading Temperature
        self._send_command(3)
        self._wait_for_conversion()
        # Wait for measurement
        #time.sleep_ms(320)
        
        msb = self._read_byte(True)
        lsb = self._read_byte(True)
        crc = self._read_byte(False)
        raw_temp = (msb << 8) | lsb
        temp_c = -40.0 + 0.01 * raw_temp

        # Read Humidity
        # self._send_start()
        # 0x05 is the command for reading Relative Humidity
        self._send_command(5)
        self._wait_for_conversion()
        #time.sleep_ms(80)
        
        msb = self._read_byte(True)
        lsb = self._read_byte(True)
        crc = self._read_byte(False)
        raw_humi = (msb << 8) | lsb
        
        # Linear conversion for Humidity
        rh_lin = -4.0 + 0.0405 * raw_humi - 2.8E-6 * (raw_humi ** 2)

        # Temperature compensation for Humidity
        rh_true = (temp_c - 25.0) * (0.01 + 80.0E-6 * raw_humi) + rh_lin

        return temp_c, min(max(rh_true, 0.0), 100.0)

# Example Usage
# sensor = SHT75(sck_pin=14, data_pin=13)
# temp, hum = sensor.r
