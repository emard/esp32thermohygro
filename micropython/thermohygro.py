from sht75 import SHT75
from sht85 import SHT85
import ssd1306txt

sensor1_scl_pin=const(3)
sensor1_sda_pin=const(4)
sensor2_scl_pin=const(1)
sensor2_sda_pin=const(2)

t1=-99.9
rh1=-99.9
t2=-99.9
rh2=-99.9
while True:
  if t1<-99:
    sensor1=SHT85(sck_pin=sensor1_scl_pin, data_pin=sensor1_sda_pin)
    if sensor1.detect()==False:
      sensor1=SHT75(sck_pin=sensor1_scl_pin, data_pin=sensor1_sda_pin)
  t1,rh1=sensor1.read_temp_humidity()    
  ssd1306txt.thdisp(1,t1,rh1)
  if t2<-99:
    sensor2=SHT85(sck_pin=sensor2_scl_pin, data_pin=sensor2_sda_pin)
    if sensor2.detect()==False:
      sensor2=SHT75(sck_pin=sensor2_scl_pin, data_pin=sensor2_sda_pin)
  t2,rh2=sensor2.read_temp_humidity()
  ssd1306txt.thdisp(2,t2,rh2)
  print("T1=%5.2f C RH1=%5.2f %% T2=%5.2f C RH2=%5.2f %% " % (t1,rh1,t2,rh2))
