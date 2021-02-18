// https://github.com/practicalarduino/SHT1x
#include <SHT1x.h>
#include <U8g2lib.h>
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0, /* clock=*/ 15, /* data=*/ 4, /* reset=*/ 16);// 
// Sensirion Sensor = Sensirion(Sensor_data[Sensor_use], Sensor_clock[Sensor_use]);
SHT1x Sensor[2] =
{ //  DATA, CLOCK
  SHT1x(21, 22),
  SHT1x(13, 23)
};

uint8_t Nsensors = 1; // 0-2 sensors present

char Ctemperature[2][10], Chumidity[2][10], Cip[20];

float Temperature[2], Humidity[2]; // x100 temperature and humidity
char IP[20];

void u8g2_prepare(void) {
  u8g2.setFont(u8g2_font_6x10_tf);
  u8g2.setFontRefHeightExtendedText();
  u8g2.setDrawColor(1);
  u8g2.setFontPosTop();
  u8g2.setFontDirection(0);
}

void u8g2_box_frame(uint8_t a) {
  u8g2.drawStr( 0, 0, "drawBox");
  u8g2.drawBox(5,10,20,10);
  u8g2.drawBox(10+a,15,30,7);
  u8g2.drawStr( 0, 30, "drawFrame");
  u8g2.drawFrame(5,10+30,20,10);
  u8g2.drawFrame(10+a,15+30,30,7);
}

void reading()
{
  digitalWrite(LED_BUILTIN, HIGH);
  #if 1
  for(int i = 0; i < 2; i++)
  {
    Temperature[i] = Sensor[i].readTemperatureC();
    Humidity[i] = Sensor[i].readHumidity();
  }
  #else
  for(int i = 0; i < 2; i++)
  {
    Temperature[i] = 0.1*((rand()%2000)-1000); // deg C
    Humidity[i] = 0.1*((rand()%1000)); // % RH
  }
  #endif
  digitalWrite(LED_BUILTIN, LOW);
}


void display1sensor(uint8_t i)
{
  if(Humidity[i] > -20.0 && Humidity[i] < 120.0)
  {
    snprintf(Ctemperature[i], sizeof(Ctemperature[0]), "%.1f%cC", Temperature[i], 0xB0);
    snprintf(Chumidity[i], sizeof(Chumidity[0]), "%.1f%%", Humidity[i]);
  }
  else
  {
    sprintf(Ctemperature[i], "___._%cC", 0xB0);
    sprintf(Chumidity[i], "___._%%");
  }
  sprintf(IP, "192.168.1.42");
  snprintf(Cip, sizeof(Cip), "%s", IP);
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_fub25_tf); // proportional
  int w;
  w = u8g2.getStrWidth(Ctemperature[i]);
  u8g2.drawStr(127-w,0,Ctemperature[i]);
  w = u8g2.getStrWidth(Chumidity[i]);
  u8g2.drawStr(127-w,29,Chumidity[i]);
  u8g2.setFont(u8g2_font_6x10_tf); // proportional
  w =  u8g2.getStrWidth(Cip);
  u8g2.drawStr(127-w,56,Cip);
  u8g2.sendBuffer();
}

void display2sensors()
{
  for(int i = 0; i < 2; i++)
  {
    if(Humidity[i] > -20.0 && Humidity[i] < 120.0)
    {
      if(i == 0)
      {
        snprintf(Ctemperature[i], sizeof(Ctemperature[0]), "%.1f%cC", Temperature[i], 0xB0);
        snprintf(Chumidity[i], sizeof(Chumidity[0]), "%.1f%%", Humidity[i]);
      }
      else
      {
        snprintf(Ctemperature[i], sizeof(Ctemperature[0]), "%.1f", Temperature[i]);
        snprintf(Chumidity[i], sizeof(Chumidity[0]), "%.1f", Humidity[i]);
      }
    }
    else
    {
      if(i == 0)
      {
        sprintf(Ctemperature[i], "___._%cC", 0xB0);
        sprintf(Chumidity[i], "___._%%");
      }
      else
      {
        sprintf(Ctemperature[i], "___._");
        sprintf(Chumidity[i], "___._");
      }
    }
  }
  sprintf(IP, "192.168.1.42");
  snprintf(Cip, sizeof(Cip), "%s", IP);  
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_fub14_tf); // proportional
  int w;
  int x = 72; // middle line
  w = u8g2.getStrWidth(Ctemperature[0]);
  u8g2.drawStr(x-w,0,Ctemperature[0]);
  w = u8g2.getStrWidth(Ctemperature[1]);
  u8g2.drawStr(127-w,0,Ctemperature[1]);
  w = u8g2.getStrWidth(Chumidity[0]);
  u8g2.drawStr(x-w,29,Chumidity[0]);
  w = u8g2.getStrWidth(Chumidity[1]);
  u8g2.drawStr(127-w,29,Chumidity[1]);
  u8g2.setFont(u8g2_font_6x10_tf); // proportional
  w =  u8g2.getStrWidth(Cip);
  u8g2.drawStr(127-w,56,Cip);
  u8g2.sendBuffer();
}

void refresh_display()
{
  #if 1
  if(Humidity[0] < -20.0 || Humidity[0] > 120.0)
  {
    display1sensor(1);
    return; 
  }
  if(Humidity[1] < -20.0 || Humidity[1] > 120.0)
  {
    display1sensor(0);
    return;
  }
  #endif
  display2sensors();
}


void setup() {
  Serial.begin(115200);
  u8g2.begin();
  u8g2_prepare();
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  static uint8_t ledstate;
  reading();
  refresh_display();
  ledstate ^= 1;
  digitalWrite(LED_BUILTIN, ledstate);
  // delay(900);
}


