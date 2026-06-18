from machine import Pin
from time import sleep_ms
from shtcrctab import crctable

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

    # crc = 0
    # crc = crctable[crc ^ x]

    # Bit reverse an 8 bit value for CRC
    def rbit8(self, v:int)->int:
      v = (v & 0x0f) << 4 | (v & 0xf0) >> 4
      v = (v & 0x33) << 2 | (v & 0xcc) >> 2
      return (v & 0x55) << 1 | (v & 0xaa) >> 1

    def crc_calc(self, status:int, cmd:int, msb:int, lsb:int)->int:
      crc = self.rbit8(status) & 0xF0
      crc = crctable[crc ^ cmd]
      crc = crctable[crc ^ msb]
      return self.rbit8(crctable[crc ^ lsb])

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
            sleep_ms(10)
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

    # T[°C], RH[%], serial_no (always 0)
    def read_temp_humidity(self)->Tuple(float,float,int):

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
          temp_c = -99.9
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
          rh_true = -99.9
          if self.verbose:
            print("bad crc reading humidity")

        return temp_c, rh_true, 0

# Example Usage
# sensor = SHT75(sck_pin=14, data_pin=13)
# temp, hum = sensor.r
