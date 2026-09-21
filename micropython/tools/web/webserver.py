# web server for TH2
# shows data on display and provides web interface
# wget https://raw.githubusercontent.com/miguelgrinberg/microdot/refs/heads/main/src/microdot/microdot.py -O microdot.py
# mpremote cp microdot.py :/lib/
# mpremote cp -r wificonnect.py th2web.py webserver.py public_html :/
# import wificonnect
# import webserver
from microdot import *
from sys import implementation
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

t1=-99.9
rh1=-99.9
model1=""
serial1=0
t2=-99.9
rh2=-99.9
model2=""
serial2=0
readout=""

app=Microdot()
Response.default_content_type='text/html'
if implementation.name=="micropython":
  # for esp32
  pass
if implementation.name=="cpython":
  # for PC
  pass

@app.get('/')
async def index(request):
  return redirect('index.html')

# request and response example:
# simple readout in one line, the same as printed on USB serial
# http://host/read
# S1=2C3A02D0 T1=28.79 C RH1=41.06 % S2=2C3A1297 T2=28.50 C RH2=41.18 %
@app.get('/line')
async def index(request):
  #port=request.args['port'] # argument "port" value 1 given like http://host/read?port=1
  return readout

# request and response example:
# readout in json format
# http://host/json
# {'serial1':0x1234,'t1':'28.03','rh1':'30.25'}
@app.get('/json')
async def index(request):
  #port=request.args['port'] # argument "port" value 1 given like http://host/json?port=1
  answer='{"serial1":%d,"t1":%.2f,"rh1":%.2f,"serial2":%d,"t2":%.2f,"rh2":%.2f}' % (serial1,t1,rh1,serial2,t2,rh2)
  return answer

# static files
@app.route('<path:path>')
async def static(request, path):
  if '..' in path:
    # directory traversal is not allowed
    return 'Not found',404
  return send_file('public_html/'+path)

# loop which constantly reads SHT75/SHT85 sensors
# during busy wait to read sensors web interface stalls
# FIXME busy wait
async def loop_sensor_read():
  global t1,rh1,model1,serial1,t2,rh2,model2,serial2,readout
  ssd1306txt.init(disp_width=display_width,disp_height=display_height,
    scl_pin=display_scl_pin,sda_pin=display_sda_pin,
    rst_pin=display_rst_pin,dc_pin=display_dc_pin,cs_pin=display_cs_pin)
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
    readout="S1=%08X T1=%5.2f C RH1=%5.2f %% S2=%08X T2=%5.2f C RH2=%5.2f %% " % (serial1,t1,rh1,serial2,t2,rh2)
    print(readout)
    await asyncio.sleep(0.1)

async def main():
  asyncio.create_task(loop_sensor_read())
  await app.start_server(port=80,debug=False) # debug=True prints http requests
  await asyncio.sleep(0.010)

asyncio.run(main())
