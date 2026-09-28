import ssd1306txt
# sensor = 1 or 2
def thdisp(sensor:int, model:str, t:float, rh:float, serial:int):
  x0=((sensor-1) & 1)*64
  xunit=47
  #boldtext=((0,0)) # thin text, not bold
  boldtext=((0,0),(0,1),(1,1),(1,0)) # bold text
  #shty=(0,16,32,56) # y-location on the screen of sensor mode, temperature, humidity, serial
  shty=(0,8,24,40) # y-location on the screen of sensor model and port number, temperature, humidity, serial
  ssd1306txt.oled.fill_rect(x0,0,x0+64,48,0)
  ssd1306txt.text("%-5s %d" % (model,sensor,), x0, shty[0], 1)
  if t>-99 and t<200:
    for bold in boldtext: # for bold text
      if t>0 and t<100:
        ssd1306txt.text("%4.1f" % (t,), x0+bold[0], shty[1]+bold[1], 1, 12, 512, 512)
      else:
        ssd1306txt.text("%4.0f" % (t,), x0+bold[0], shty[1]+bold[1], 1, 12, 512, 512)
      if rh>0 and rh<100:
        ssd1306txt.text("%4.1f" % (rh,), x0+bold[0],shty[2] +bold[1], 1, 12, 512, 512)
      else:
        ssd1306txt.text("%4.0f" % (rh,), x0+bold[0], shty[2]+bold[1], 1, 12, 512, 512)
    ssd1306txt.text("°C", x0+xunit, shty[1],1)
    ssd1306txt.text("%", x0+xunit, shty[2], 1)
    if serial:
      ssd1306txt.text("%08X" % (serial,), x0, shty[3], 1)
  ssd1306txt.oled.show()

def netdisp(ipaddr:str, datestr:str):
  ssd1306txt.oled.fill_rect(0,48,128,64,0)
  shty=(49,57) # y-location on the screen ip address, time
  ssd1306txt.text(ipaddr,  0, shty[0], 1)
  ssd1306txt.text(datestr, 0, shty[1], 1)
  ssd1306txt.oled.show()
