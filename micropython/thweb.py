# web server for TH2
# this is main and full-featured application for TH2
# shows data on display and provides web interface

# installation quick notes
# mkdir -p lib
# wget https://raw.githubusercontent.com/miguelgrinberg/microdot/refs/heads/main/src/microdot/microdot.py -O lib/microdot.py
# mpremote cp lib/microdot.py :/lib/
# mpremote cp -r *.py public_html :/
from microdot import *
from sys import implementation
from sht75 import SHT75
from sht85 import SHT85
from time import localtime
import os,network,ntptime
import thpinout,thwificfg,thlogcfg,ssd1306txt

logfile="/public_html/thlog.csv"

t1=-99.9
rh1=-99.9
model1=""
serial1=0
t2=-99.9
rh2=-99.9
model2=""
serial2=0
readout=""
track_hour_before=-1

def wificonnect():
  global wifi
  wifi=network.WLAN(network.STA_IF)
  wifi.active(True)
  #wifi.config(txpower=13)
  wifi.connect(thwificfg.USER, thwificfg.PASS)
  #print("show IP address:")
  #print("webserver.wifi.ifconfig()")
  #ntptime.settime() # call it when connected - error if no internet

# returns storage bytes free
def storagefree()->int:
  stat=os.statvfs("/")
  return stat[0]*stat[3]

def log2file():
  global track_hour_before
  time_now=localtime() # sample time now
  hour_now=time_now[3] # 3 is integer hour, 4 is integer minute
  if time_now[0]<2020 or hour_now==track_hour_before:
    return
  # this code is executed every hour
  if hour_now==4:
    # at 04:00 resync time with ntp
    if wifi.isconnected():
      if wifi.ifconfig()[0]!="0.0.0.0":
        try:
          ntptime.settime()
        except:
          pass
  if hour_now not in thlogcfg.loghours:
    return
  # triggers log at start of a new hour
  track_hour_before=hour_now # prevents double log at same hour
  try:
    with open(logfile, "r") as file:
      #print(f"File {logfile} exists and can be read.")
      file.close()
      with open(logfile, "a") as file:
        #print(f"File {logfile} exists and can be appended.")
        try:
          # datetime,ip,serial1,t1,rh1,serial2,t2,rh2
          logline='"%04d-%02d-%02d %02d:%02d:%02d" ' % time_now[0:6]
          logline+=f"{wifi.ifconfig()[0]} "
          logline+=f"{serial1:08X} {t1:.2f} {rh1:.2f} {serial2:08X} {t2:.2f} {rh2:.2f}\n"
          file.write(logline)
          #print(f"Appending to {logfile} successful.")      
        except:
          #print(f"Appending to {logfile} failed.")      
          pass
  except:
    #print(f"File {logfile} does not exist.")
    #print(f"creating {logfile}.")
    try:
      with open(logfile, "a") as file:
        # write first 2 lines as the file header
        file.write('"DATETIME" "ADDR" "SERIAL1" "T1" "RH1" "SERIAL2" "T2" "RH2"\n')
        file.write('"[UTC]" "[IP]" "[HEX]" "[°C]" "[%]" "[HEX]" "[°C]" "[%]"\n')
        #print(f"File {logfile} created.")
    except:
      #print(f"Create {logfile} failed.")
      pass

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
  answer='{"datetime":"%04d-%02d-%02dT%02d:%02d:%02dZ",' % localtime()[0:6]
  answer+=f'"serial1":{serial1},"t1":{t1:.2f},"rh1":{rh1:.2f},"serial2":{serial2},"t2":{t2:.2f},"rh2":{rh2:.2f},'
  answer+=f'"free":{storagefree()}'
  answer+='}\n'
  #  answer+='"serial1":%d,"t1":%.2f,"rh1":%.2f,"serial2":%d,"t2":%.2f,"rh2":%.2f}' % (serial1,t1,rh1,serial2,t2,rh2)
  return answer

# reads/sets integer hours [UTC] in a day when to log
# http://host/log
# http://host/log?hours=5,8,10
@app.get('/log')
async def index(request):
  try:
    hours_str=request.args['hours'].strip().strip(",") # argument "hours" given like http://host/log?hours=2,5,12
  except:
    # without argument returs existing log setting
    return str(thlogcfg.loghours)[1:-1] # tuple without brackets
  if hours_str=="":
    hours_tuple=()
  else:
    hours_tuple=tuple(map(int,hours_str.split(',')))
  thlogcfg.loghours=hours_tuple
  try:
    with open("thlogcfg.py","w") as cfgfile:
      try:
        cfgfile.write("# comma separated list of integer hours [UTC] when to write log every day\n")
        cfgfile.write(f"loghours={str(hours_tuple)}\n")
      except:
        return "FAIL"
  except:
    pass
  return str(thlogcfg.loghours)[1:-1] # tuple without brackets

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
  ssd1306txt.init(disp_width=thpinout.display_width,disp_height=thpinout.display_height,
    scl_pin=thpinout.display_scl_pin,sda_pin=thpinout.display_sda_pin,
    rst_pin=thpinout.display_rst_pin,dc_pin=thpinout.display_dc_pin,cs_pin=thpinout.display_cs_pin)
  while True:
    if localtime()[0]<2020:
      if wifi.isconnected():
        if wifi.ifconfig()[0]!="0.0.0.0":
          try:
            ntptime.settime()
          except:
            pass
    local_time=localtime()
    if t1<-99:
      model1="SHT85"
      sensor1=SHT85(sck_pin=thpinout.sensor1_scl_pin, data_pin=thpinout.sensor1_sda_pin)
      if sensor1.detect()==False:
        model1="SHT75"
        sensor1=SHT75(sck_pin=thpinout.sensor1_scl_pin, data_pin=thpinout.sensor1_sda_pin, chip_v=4)
    t1,rh1,serial1=sensor1.read_temp_humidity()    
    if t1<-99:
      model1=""
    ssd1306txt.thdisp(1,model1,t1,rh1,serial1)
    if t2<-99:
      model2="SHT85"
      sensor2=SHT85(sck_pin=thpinout.sensor2_scl_pin, data_pin=thpinout.sensor2_sda_pin)
      if sensor2.detect()==False:
        model2="SHT75"
        sensor2=SHT75(sck_pin=thpinout.sensor2_scl_pin, data_pin=thpinout.sensor2_sda_pin, chip_v=4)
    t2,rh2,serial2=sensor2.read_temp_humidity()
    if t2<-99:
      model2=""
    ssd1306txt.thdisp(2,model2,t2,rh2,serial2)
    readout="%04d-%02d-%02dT%02d:%02d:%02dZ " % local_time[0:6]
    readout+="%s S1=%08X T1=%5.2f C RH1=%5.2f %% S2=%08X T2=%5.2f C RH2=%5.2f %% " % (wifi.ifconfig()[0],serial1,t1,rh1,serial2,t2,rh2,)
    readout+="FREE=%d bytes" % (storagefree(),)
    print(readout)
    log2file()
    while local_time[5]==localtime()[5]: # wait until next second
      await asyncio.sleep(0.5) # for SHT75 max 1 measurement per second

async def main():
  asyncio.create_task(loop_sensor_read())
  await app.start_server(port=80,debug=False) # debug=True prints http requests
  await asyncio.sleep(0.010)

wificonnect()
asyncio.run(main())
