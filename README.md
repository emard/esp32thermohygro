# THERMOHYGROMETER

ESP32 2-channel SHT75/SHT85 thermohygrometer logger with OLED display
and web interface.

New Micropython version is recommended and full featured.

Old code for Arduino in directory heltec_kit_thermohygro supports SHT75 only.

# Install

Install Microypthon for ESP32-S3:

    pipx install esptool
    wget https://micropython.org/resources/firmware/ESP32_GENERIC_S3-SPIRAM_OCT-20260824-v1.29.0.bin
    esptool.py --port /dev/ttyACM0 --baud 460800 write_flash 0 ESP32_GENERIC_S3-SPIRAM_OCT-20260824-v1.29.0.bin

Install Thermohygrometer:

    pipx install mpremote
    mkdir -p lib
    wget https://raw.githubusercontent.com/miguelgrinberg/microdot/refs/heads/main/src/microdot/microdot.py -O lib/microdot.py
    mpremote cp lib/microdot.py :/lib/
    mpremote cp -r *.py public_html :/

Install pye editor:

    mpremote mip install github:robert-hh/Micropython-Editor

Edit file "thwificfg.py" to enter WiFi access point username and password.
Thermologger needs internet access to set real time clock (RTC). Most
ESP32 boards usually don't have RTC running on battery.
