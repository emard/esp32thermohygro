from machine import Pin
#from time import sleep_us

import machine
import time


class SHT75:
    def __init__(self, sck_pin, data_pin):
        self.sck = Pin(sck_pin, Pin.OUT)
        self.data = Pin(data_pin, mode=Pin.OPEN_DRAIN, pull=Pin.PULL_UP)
        self.data.value(1)
        self.sck.value(0)

    CMD_READ_TEMPERATURE=const(3)
    CMD_READ_HUMIDITY=const(5)
    CMD_READ_STATUS=const(7)

    verbose=False

    crctable = bytearray([0, 49,
98, 83, 196, 245, 166, 151, 185, 136, 219,
234, 125, 76, 31, 46, 67, 114, 33, 16, 135,
182, 229, 212, 250, 203, 152, 169, 62, 15,
92, 109, 134, 183, 228, 213, 66, 115, 32,
17, 63, 14, 93,108, 251, 202, 153, 168,
197, 244, 167, 150, 1, 48, 99, 82, 124, 77,
30, 47, 184, 137, 218, 235, 61, 12, 95,
110, 249, 200, 155, 170, 132, 181, 230,
215, 64, 113, 34, 19, 126, 79, 28, 45, 186,
139, 216, 233, 199, 246, 165, 148, 3, 50,
97, 80, 187, 138, 217, 232, 127, 78, 29,
44, 2, 51, 96, 81, 198, 247, 164, 149, 248,
201, 154, 171, 60, 13, 94, 111, 65, 112,
35, 18, 133, 180, 231, 214, 122, 75, 24,
41, 190, 143, 220, 237, 195, 242, 161, 144,
7, 54, 101, 84, 57, 8, 91, 106, 253, 204,
159, 174, 128, 177, 226, 211, 68, 117, 38,
23, 252, 205, 158, 175, 56, 9, 90, 107, 69,
116, 39, 22, 129, 176, 227, 210, 191, 142,
221, 236, 123, 74, 25, 40, 6, 55, 100, 85,
194, 243, 160, 145, 71, 118, 37, 20, 131,
178, 225, 208, 254, 207, 156, 173, 58, 11,
88, 105, 4, 53, 102, 87, 192, 241, 162,
147, 189, 140, 223, 238, 121, 72, 27, 42,
193, 240, 163, 146, 5, 52, 103, 86, 120,
73, 26, 43, 188, 141, 222, 239, 130, 179,
224, 209, 70, 119, 36, 21, 59, 10, 89, 104,
255, 206, 157, 172])
    # crc = 0
    # crc = crctable[crc ^ x]

    # Bit reverse an 8 bit value for CRC
    def rbit8(self, v:int)->int:
      v = (v & 0x0f) << 4 | (v & 0xf0) >> 4
      v = (v & 0x33) << 2 | (v & 0xcc) >> 2
      return (v & 0x55) << 1 | (v & 0xaa) >> 1

    def crc_calc(self, status:int, cmd:int, msb:int, lsb:int)->int:
      crc = self.rbit8(status) & 0xF0
      crc = self.crctable[crc ^ cmd]
      crc = self.crctable[crc ^ msb]
      return self.rbit8(self.crctable[crc ^ lsb])

    def _send_command(self, cmd)->int:
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
        #self.data.init(mode=Pin.OPEN_DRAIN, pull=Pin.PULL_UP)
        self.sck.value(1)
        ack = self.data.value()
        self.sck.value(0)
        if ack != 0:
          if self.verbose:
            print("Sensor did not acknowledge command")

    def _wait_for_conversion(self):
        timeout = 0
        while self.data.value() != 0:
            time.sleep_ms(10)
            timeout += 10
            if timeout > 300:
                if self.verbose:
                  print("Sensor conversion timeout")
                break

    def _read_byte(self, ack):
        byte = 0
        for i in range(8):
            self.sck.value(1)
            byte = (byte << 1) | self.data.value()
            self.sck.value(0)
            
        # Send Acknowledge
        self.data.value(not ack)
        self.sck.value(1)
        self.sck.value(0)
        self.data.value(1)
        return byte

    def read_temp_humidity(self):
        # Read status register
        cmd=CMD_READ_STATUS
        ack=self._send_command(cmd)
        status = self._read_byte(True)
        crc = self._read_byte(False)

        # Read Temperature
        # 0x03 is the command for reading Temperature
        cmd=CMD_READ_TEMPERATURE
        self._send_command(cmd)
        self._wait_for_conversion()
        # Wait for measurement
        #time.sleep_ms(320)
        
        msb = self._read_byte(True)
        lsb = self._read_byte(True)
        crc = self._read_byte(False)
        crc_check = self.crc_calc(status,cmd,msb,lsb)
        raw_temp = (msb << 8) | lsb
        if crc == crc_check:
          temp_c = -40.0 + 0.01 * raw_temp
        else:
          temp_c = -99.0
          if self.verbose:
            print("bad crc reading temperature")

        # Read Humidity
        # self._send_start()
        # 0x05 is the command for reading Relative Humidity
        cmd=CMD_READ_HUMIDITY
        self._send_command(cmd)
        self._wait_for_conversion()
        #time.sleep_ms(80)

        msb = self._read_byte(True)
        lsb = self._read_byte(True)
        crc = self._read_byte(False)
        crc_check = self.crc_calc(status,cmd,msb,lsb)
        raw_humi = (msb << 8) | lsb
        
        # Linear conversion for Humidity
        rh_lin = -4.0 + 0.0405 * raw_humi - 2.8E-6 * (raw_humi ** 2)

        # Temperature compensation for Humidity
        if crc == crc_check:
          rh_true = (temp_c - 25.0) * (0.01 + 80.0E-6 * raw_humi) + rh_lin
        else:
          rh_true = -99.0
          if self.verbose:
            print("bad crc reading humidity")

        return temp_c, min(max(rh_true, 0.0), 100.0)

# Example Usage
# sensor = SHT75(sck_pin=14, data_pin=13)
# temp, hum = sensor.r
