from sht75 import SHT75
import ssd1306txt

sensor1=SHT75(sck_pin=3, data_pin=4)
sensor2=SHT75(sck_pin=1, data_pin=2)

while True:
  t1,rh1=sensor1.read_temp_humidity()
  ssd1306txt.thdisp(1,t1,rh1)
  t2,rh2=sensor2.read_temp_humidity()
  ssd1306txt.thdisp(2,t2,rh2)
  print("T1=%5.2f C RH1=%5.2f %% T1=%5.2f C RH1=%5.2f %% " % (t1,rh1,t2,rh2))
