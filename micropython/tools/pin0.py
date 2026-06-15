from machine import Pin
from time import sleep

while True:
  print(Pin(0).value())
  sleep(0.2)

  