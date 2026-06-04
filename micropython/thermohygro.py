from sht75 import SHT75
import display

sensor1=SHT75(sck_pin=3, data_pin=4)
sensor2=SHT75(sck_pin=1, data_pin=2)

while True:
  t1,rh1=sensor1.read_temp_humidity()
  t2,rh2=sensor2.read_temp_humidity()
  print("T1=%5.2f C RH1=%5.2f %% T1=%5.2f C RH1=%5.2f %% " % (t1,rh1,t2,rh2))
  display.display_t_rh(t1,rh1,t2,rh2)
