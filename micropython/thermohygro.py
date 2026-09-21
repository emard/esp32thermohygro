# simple reader app, low memory requirement
# shows result on display and prints on USB serial
# no web interface
from sht75 import SHT75
from sht85 import SHT85
import ssd1306txt

sensor1_scl_pin=const(3)
sensor1_sda_pin=const(4)
sensor2_scl_pin=const(1)
sensor2_sda_pin=const(2)

display_width=const(128)
display_height=const(64)
display_scl_pin=const(7)
display_sda_pin=const(8)
display_rst_pin=const(9)
display_dc_pin=const(6)
display_cs_pin=const(5)

ssd1306txt.init(disp_width=display_width,disp_height=display_height,
scl_pin=display_scl_pin,sda_pin=display_sda_pin,
rst_pin=display_rst_pin,dc_pin=display_dc_pin,cs_pin=display_cs_pin)

t1=-99.9
rh1=-99.9
model1=""
t2=-99.9
rh2=-99.9
model2=""
while True:
  if t1<-99:
    model1="SHT85"
    sensor1=SHT85(sck_pin=sensor1_scl_pin, data_pin=sensor1_sda_pin)
    if sensor1.detect()==False:
      model1="SHT75"
      sensor1=SHT75(sck_pin=sensor1_scl_pin, data_pin=sensor1_sda_pin, chip_v=4)
  t1,rh1,serial1=sensor1.read_temp_humidity()    
  if t1<-99:
    model1=""
  ssd1306txt.thdisp(1,model1,t1,rh1,serial1)
  if t2<-99:
    model2="SHT85"
    sensor2=SHT85(sck_pin=sensor2_scl_pin, data_pin=sensor2_sda_pin)
    if sensor2.detect()==False:
      model2="SHT75"
      sensor2=SHT75(sck_pin=sensor2_scl_pin, data_pin=sensor2_sda_pin, chip_v=4)
  t2,rh2,serial2=sensor2.read_temp_humidity()
  if t2<-99:
    model2=""
  ssd1306txt.thdisp(2,model2,t2,rh2,serial2)
  print("S1=%08X T1=%5.2f C RH1=%5.2f %% S2=%08X T2=%5.2f C RH2=%5.2f %% " % (serial1,t1,rh1,serial2,t2,rh2))
