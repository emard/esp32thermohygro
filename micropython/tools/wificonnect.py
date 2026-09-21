# simple connect as client to AP
# for small web server like microdot
import network
NAME="ra"
PASS="GigabyteBrix"
wifi=network.WLAN(network.STA_IF)
wifi.active(True)
#wifi.config(txpower=13)
wifi.connect(NAME, PASS)
print("show IP address:")
print("wificonnect.wifi.ifconfig()")
