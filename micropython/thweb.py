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
import thpinout,thwificfg,thlogcfg,thname,ssd1306txt

logfilef="/public_html/thlog%04d.csv"

t1=-99.9
rh1=-99.9
model1=""
serial1=0
t2=-99.9
rh2=-99.9
model2=""
serial2=0
readout=""
track_basis_before=-1 # initial negative value is always different than any actual value
track_hours_before=-1 # initial negative value is always different than any actual value
log_basis=5 # 3:daily 4:hourly 5:minutely

def reset_wifi():
  for a in (False, True):
    wifi.active(a)
    while wifi.active()!=a:
      pass

def wificonnect():
  global wifi
  if 1:
    # temporary enter AP mode to reset wifi
    # sometimes wifi is stubborn and won't connect even with this
    wifi=network.WLAN(network.AP_IF)
    reset_wifi()
    wifi.config(channel=1, txpower=14, essid="TH2", password="PASS")
    reset_wifi()
  wifi=network.WLAN(network.STA_IF)
  reset_wifi()
  wifi.config(dhcp_hostname=thname.HOSTNAME)
  wifi.connect(thwificfg.USER, thwificfg.PASS)
  #print("show IP address:")
  #print("webserver.wifi.ifconfig()")
  #ntptime.settime() # call it when connected - error if no internet

# returns storage bytes free
def storagefree()->int:
  stat=os.statvfs("/")
  return stat[0]*stat[3]

def logline()->str:
  # datetime,ip,serial1,t1,rh1,serial2,t2,rh2
  line='"%04d-%02d-%02d %02d:%02d:%02d" ' % localtime()[0:6]
  line+=f"{wifi.ifconfig()[0]} "
  line+=f"{serial1:08X} {t1:.2f} {rh1:.2f} {serial2:08X} {t2:.2f} {rh2:.2f}\n"
  return line

def daily_ntp_sync(hour_now:int,hour_sync:int):
  global track_hours_before
  # this code is executed on daily basis to sync clock with NTP
  if hour_now!=track_hours_before:
    track_hours_before=hour_now
    if hour_now==hour_sync: # daily at 4 o'clock
      # at 04:00 resync time with ntp
      if wifi.isconnected():
        if wifi.ifconfig()[0]!="0.0.0.0":
          try:
            ntptime.settime()
          except:
            pass

# array of strings with log files
def logfiles():
  logfilez=[]
  for filename in os.listdir("/public_html"):
    if filename.startswith("thlog"):
      logfilez.append(filename)
  logfilez.sort()
  return logfilez

def logfiles_str():
  return str(logfiles()).replace("'",'"') # BUG if any filename contains " or '

# remove oldest logs until minfree bytes
def remove_old_log(minfree=65536):
  for file in logfiles():
    if storagefree()>=minfree:
      return
    os.unlink("/public_html/"+file)

def log2file():
  global track_basis_before
  time_now=localtime() # sample time now
  basis_now=time_now[thlogcfg.basis] # 3:daily, 4:hourly, 5:minutely
  if time_now[0]<2020: # clock is not synchronized (usually 2000)
    return
  daily_ntp_sync(time_now[3],4) # sync every day at 4 o'clock UTC
  if basis_now==track_basis_before:
    return
  # this code is executed on log basis
  # if log basis is daily, it is executed every hour
  if basis_now not in thlogcfg.events:
    return
  # delete oldest log file(s) until 64K is free
  remove_old_log()
  logfile=logfilef % (time_now[0],) # year in filename
  # this code is executed on log list
  track_basis_before=basis_now # prevents double log at same hour
  try:
    with open(logfile, "r") as file:
      #print(f"File {logfile} exists and can be read.")
      file.close()
      with open(logfile, "a") as file:
        #print(f"File {logfile} exists and can be appended.")
        try:
          file.write(logline())
          #print(f"Appending to {logfile} successful.")      
          file.close()
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
        file.write(logline())
        #print(f"File {logfile} created.")
        file.close()
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
# http://host/line
# S1=2C3A02D0 T1=28.79 C RH1=41.06 % S2=2C3A1297 T2=28.50 C RH2=41.18 %
@app.get('/line')
async def index(request):
  #port=request.args['port'] # argument "port" value 1 given like http://host/read?port=1
  return readout

# request and response example:
# readout in json format
# http://host/read
# {'serial1':0x1234,'t1':'28.03','rh1':'30.25'}
@app.get('/read')
async def index(request):
  #port=request.args['port'] # argument "port" value 1 given like http://host/json?port=1
  answer='{"datetime":"%04d-%02d-%02dT%02d:%02d:%02dZ",' % localtime()[0:6]
  answer+=f'"serial1":{serial1},"t1":{t1:.2f},"rh1":{rh1:.2f},"serial2":{serial2},"t2":{t2:.2f},"rh2":{rh2:.2f},'
  answer+=f'"free":{storagefree()}'
  answer+='}\n'
  #  answer+='"serial1":%d,"t1":%.2f,"rh1":%.2f,"serial2":%d,"t2":%.2f,"rh2":%.2f}' % (serial1,t1,rh1,serial2,t2,rh2)
  return answer

# returns log status as JSON string
def logstatus()->str:
  logevents=str(thlogcfg.events)[1:-1].strip().strip(",") # tuple without brackets then strip " " and ","
  return '{"basis":%d,"events":"%s","files":%s}' % (thlogcfg.basis,logevents,logfiles_str()) # json

# reads/sets integer hours [UTC] in a day when to log
# http://host/log
# http://host/log?basis=3&list=5,8,10
@app.get('/log')
async def index(request):
  try:
    basis_str=request.args['basis'].strip().strip(",") # argument "list" given like http://host/log?list=2,5,12
  except:
    basis_str=""
  try:
    list_str=request.args['events'].strip().strip(",") # argument "list" given like http://host/log?list=2,5,12
  except:
    list_str=""
  if basis_str=="" and list_str=="":
    return logstatus()
  if basis_str=="":
    basis_int=3 # default is logging on daily basis
  else:
    basis_int=int(basis_str)
  if list_str=="":
    list_tuple=()
  else:
    list_tuple=tuple(map(int,list_str.split(',')))
  thlogcfg.basis=basis_int
  thlogcfg.events=list_tuple
  try:
    with open("thlogcfg.py","w") as cfgfile:
      try:
        cfgfile.write("# log basis 1:yearly 2:monthly 3:daily 4:hourly 5:minutely\n")
        cfgfile.write(f"basis={basis_int}\n")
        cfgfile.write("# when to write log\n")
        cfgfile.write("# hours are in UTC (GMT) time zone\n")
        cfgfile.write("# comma separated list of integer sub-basis months/days/hours/minutes/econds\n")
        cfgfile.write(f"events={str(list_tuple)}\n")
      except:
        return "FAIL"
  except:
    pass
  return logstatus()

# static files
@app.route('<path:path>')
async def static(request, path):
  # print(f"sending file {path}\n")
  if '..' in path:
    # directory traversal is not allowed
    return ('Not found',404)
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
      await asyncio.sleep(0.2) # for SHT75 max 1 measurement per second

async def main():
  asyncio.create_task(loop_sensor_read())
  await app.start_server(port=80,debug=False) # debug=True prints http requests
  await asyncio.sleep(0.010)

wificonnect()
asyncio.run(main())
