#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <AsyncJson.h>
#include <AsyncMessagePack.h>
#include <ESPAsyncWebServer.h>
#include "WiFi.h"
#include "time.h"

// WiFi credentials.
const char* WIFI_SSID = "INSERT WIFI SSID";
const char* WIFI_PASS = "INSERT WIFI PASSWORD";                                                                                                                                                                                                                               

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define PIN_TEMPERATURE_SENSOR 5
#define PIN_LIGHT_SENSOR 34
#define PIN_FUNCTIONAL_LED 26 // Green LED
#define PIN_ERROR_LED 32 // Red LED
#define PIN_INFORMATIONAL_LED 33 // Blue LED
#define PIN_LEFT_BUTTON 25 // White Button
#define PIN_MID_BUTTON 27 // Yellow Button
#define PIN_RIGHT_BUTTON 12 // White Button

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

DHT dht(PIN_TEMPERATURE_SENSOR, DHT11);
static AsyncWebServer server(4719); // Port: 4719
static AsyncCorsMiddleware cors;

int humidity;                                                                                       
int temperature;
float light;
int light_percentage;
int heatIndex;
float voltage;

int midButtonState;
int rightButtonState;
int leftButtonState;
int lastMidButtonState;
int lastRightButtonState;
int lastLeftButtonState;

enum button {
  LEFT,
  MID,
  RIGHT
};

String all_mode[3] = {"Menu", "Sensor", "Stop"};
int mode = 0;
int selectedMode = 0;
float lastDebounceTime;
float debounceDelay = 50;

bool lightDisabled = false;
bool disabled = false;



// Utility Classes

void LoadingScreenDisplay(String message, String secondMessage = "", bool waitText = true) { // FIX POSITIONS IN FUTURE
  display.clearDisplay();
  int16_t x1, y1;
  uint16_t w, h;
  float width = display.width();
  float height = display.height();
  display.setTextColor(WHITE);

  int msgHeight, secMsgHeight, waitHeight = 0;

  if (waitText == false && secondMessage == "") {
    msgHeight = 0;
  }
  else if (waitText == false) {
    msgHeight = (height / 2) - 10;
    secMsgHeight = (height / 2) + 10;
  }
  else if (secondMessage == "") {
    msgHeight = (height / 2) - 15;
    waitHeight = (height / 2) + 15;
  }
  else {
    msgHeight = (height / 2) - 20;
    secMsgHeight = (height / 2) - 10;
    waitHeight = (height / 2) + 10;
  }

  if (message == "") {
    display.getTextBounds(message, 0, msgHeight, &x1, &y1, &w, &h);
    display.setCursor((width - w) / 2, (height - h));
    display.print(message);
  }

  if (secondMessage != "") {
    display.getTextBounds(secondMessage, 0, secMsgHeight, &x1, &y1, &w, &h);
    display.setCursor((width - w) / 2, (height - h) - msgHeight);
    display.print(secondMessage);
  }

  if (waitText == true) {
    display.getTextBounds("Please wait...", 0, waitHeight, &x1, &y1, &w, &h);
    display.setCursor((width - w) / 2 - 1, h);
    display.print("Please wait...");
  }
  
  display.display();
}

void connectToWiFi() {
    int tries = 0; // 15 tries before reconnect

    if (WiFi.status() != WL_CONNECTED) {
      // Set WiFi to station mode and disconnect from an AP if it was previously connected
      WiFi.mode(WIFI_STA);
      WiFi.begin(WIFI_SSID, WIFI_PASS);
      delay(1000);
    }
  
    while (WiFi.status() != WL_CONNECTED) {
      if (tries > 15) {
        WiFi.disconnect();
        delay(500);
        tries = 0;
        WiFi.mode(WIFI_STA);
        WiFi.begin(WIFI_SSID, WIFI_PASS);
        delay(1000);
      }

      if (!lightDisabled) {
        digitalWrite(PIN_ERROR_LED, HIGH);
        digitalWrite(PIN_INFORMATIONAL_LED, HIGH);
        digitalWrite(PIN_FUNCTIONAL_LED, HIGH);
      }
      delay(1000);
      tries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      if (!lightDisabled) {
        digitalWrite(PIN_ERROR_LED, LOW);
        digitalWrite(PIN_INFORMATIONAL_LED, LOW);
        digitalWrite(PIN_FUNCTIONAL_LED, LOW);
      }
      tries = 0;
    }
}

void disabledToggle(String toToggle) {
  if (toToggle == "all") {
    if (disabled == false) {
      disabled = true;
      display.clearDisplay();
      display.setTextColor(WHITE);
      display.setCursor(30, 10);
      display.print("Device is\n    deactivated.");
      display.setCursor(15, 40);
      display.print("Press Button to\n    activate it.");
      display.display();

      digitalWrite(PIN_ERROR_LED, LOW);
      digitalWrite(PIN_FUNCTIONAL_LED, LOW);
      digitalWrite(PIN_INFORMATIONAL_LED, LOW);
      WiFi.disconnect();
      delay(300);
    }
    else {
      disabled = false;

      display.clearDisplay();
      display.setTextColor(WHITE);
      display.setCursor(20, 10);
      display.print("Please wait...");
      display.display();

      connectToWiFi();
      delay(300);
    }
  }

  else if (toToggle == "light") {
    if (lightDisabled == false) {
      lightDisabled = true;

      digitalWrite(PIN_ERROR_LED, LOW);
      digitalWrite(PIN_FUNCTIONAL_LED, LOW);
      digitalWrite(PIN_INFORMATIONAL_LED, LOW);
      delay(300);
    }
    else {
      lightDisabled = false;
      delay(300);
    }
  }
  delay(200);
}

// Debounce logic to remove unwanted input noise and using the button state properly
void debounce (int reading, enum button btnType, int& buttonState, int& lastButtonState) {
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    int size = sizeof(all_mode) / sizeof(all_mode[0]);

    if (reading != buttonState) {
      buttonState = reading;
      if (buttonState == HIGH) {

        if (btnType == LEFT) {
          selectedMode--;

          if (selectedMode < 0) {
            selectedMode = size - 1; // Array starts at 0
          }
        }
        else if (btnType == RIGHT) {
          selectedMode++;

          if (selectedMode > size - 1) { // Array starts at 0
            selectedMode = 0;
          }
        }
        else if (btnType == MID) {
          // Check if was disabled before and enable then
          if (mode == 2) {
            disabledToggle("all");
          }

          // Return to *Start* of Main Menu
          if (mode != 0) {
            selectedMode = 0;
          }

          mode = selectedMode; // Select selected Option
  
          // Run function to toggle disable just once. Thats why here.
          if (mode == 2) {
            disabledToggle("all");
          }
        }
      }
    }
  }

  lastButtonState = reading;
}



// Process Functions

void setup() {
  pinMode(PIN_ERROR_LED, OUTPUT);
  pinMode(PIN_FUNCTIONAL_LED, OUTPUT);
  pinMode(PIN_INFORMATIONAL_LED, OUTPUT);
  pinMode(PIN_LEFT_BUTTON, INPUT);
  pinMode(PIN_MID_BUTTON, INPUT);
  pinMode(PIN_RIGHT_BUTTON, INPUT);
  pinMode(PIN_TEMPERATURE_SENSOR, INPUT);
  pinMode(PIN_LIGHT_SENSOR, INPUT);
  dht.begin();

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {    
    digitalWrite(PIN_FUNCTIONAL_LED, HIGH); // Turns on Error LED for 120 secs | ignores lightDisabled because its importance
    delay(120000);
  }
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setCursor(10, 10);
  display.print("CONNECTING TO WIFI");
  display.setCursor(20, 25);
  display.print("Please wait...");
  display.display();

  connectToWiFi();

  server.addMiddleware(&cors);

  server.on("/test", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain", "Hello, world");
  });

  server.on("/lightToggle", HTTP_GET, [](AsyncWebServerRequest *request) {
    JsonDocument doc;
    doc["name"] = "light";
    doc["status"] = (!lightDisabled); // True = Light is on
    String output;
    serializeJson(doc, output);
    request->send(200, "application/json", output);
  });

  server.on("/getMode", HTTP_GET, [](AsyncWebServerRequest *request) {
    JsonDocument doc;
    doc["name"] = "modus";
    doc["modus"] = String(mode);
    doc["selected"] = String(selectedMode);
    String output;
    serializeJson(doc, output);
    request->send(200, "application/json", output);
  });

  server.on("/lightToggle", HTTP_POST, [](AsyncWebServerRequest *request) {
    bool before = (!lightDisabled);
    disabledToggle("light");
    delay(200);

    JsonDocument doc;
    doc["name"] = "light";
    doc["before"] = before;
    doc["status"] = (!lightDisabled); // True = Light is on
    String output;
    serializeJson(doc, output);
    request->send(200, "application/json", output);
  });
 
  server.on("/humidity", HTTP_GET, [](AsyncWebServerRequest *request) {
    JsonDocument doc; 

    doc["value"] = String(humidity);
    doc["unit"] = "%";

    String output;
    serializeJson(doc, output);
    
    request->send(200, "application/json", output);
  });

  server.on("/temperature", HTTP_GET, [](AsyncWebServerRequest *request) {
    JsonDocument doc; 

    doc["value"] = String(temperature);
    doc["unit"] = "°C";

    String output;
    serializeJson(doc, output);
    
    request->send(200, "application/json", output);
  });

  server.on("/heatIndex", HTTP_GET, [](AsyncWebServerRequest *request) {
    JsonDocument doc; 

    doc["value"] = String(heatIndex);
    doc["unit"] = "°C";

    String output;
    serializeJson(doc, output);
    
    request->send(200, "application/json", output);
  });

  server.on("/voltage", HTTP_GET, [](AsyncWebServerRequest *request) {
    JsonDocument doc; 
    // Five -> value = 5V | Three = 3V | raw = 0-1023
    doc["raw"] = String(voltage);
    // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
    doc["value"] = String(voltage * (5.0 / 1023.0)); // if 5V
    doc["three"] = String(voltage * (3.3 / 1023.0)); // if 3V
    doc["unit"] = "V";

    String output;
    serializeJson(doc, output);
    
    request->send(200, "application/json", output);
  });


  server.on("/light", HTTP_GET, [](AsyncWebServerRequest *request) {
    JsonDocument doc; 

    doc["value"] = String(light_percentage); // Value in %
    doc["unit"] = "%";
    doc["raw"] = String(int(light)); // raw Value (0-4095)
    doc["raw_unit"] = "lm";

    String output;
    serializeJson(doc, output);
    
    request->send(200, "application/json", output);
  });

  server.begin(); // 192.168.?.1
}

void updateDisplay() {
  display.clearDisplay();
  int16_t x1, y1;
  uint16_t w, h;
  float width = display.width();
  display.setTextWrap(false);
  display.setTextColor(WHITE);

  display.getTextBounds("Mini-Dahsboard:", 0, 0, &x1, &y1, &w, &h);
  display.setCursor((width - w) / 2, 0);
  display.print("Mini-Dahsboard:");

  // display.print("\nModus: " + String(modus));   Dont need it atm
  IPAddress ip = WiFi.localIP();
  String wifiText = "\nIP: " + String(ip[0]) + "." + String(ip[1]) + "." + String(ip[2]) + "." + String(ip[3]) + "  " + ((WiFi.status() == WL_CONNECTED) ? "+" : "-"); // Wifi Connected = + | Wifi not connected = - | Example: "IP: 192.168.100.1  +"
  display.getTextBounds(wifiText, 0, 10, &x1, &y1, &w, &h);
  display.setCursor((width - w) / 2, 10);
  display.print(wifiText);

   if (mode == 0) {
    int size = sizeof(all_mode) / sizeof(all_mode[0]);
    int16_t x2, x3;

    display.getTextBounds(String(all_mode[(selectedMode - 1 + size) % size]), width / 3, 33, &x2, &y1, &w, &h);
    display.setCursor(5, 33);
    display.print(String(all_mode[(selectedMode - 1 + size) % size]));
    display.setCursor(w, 44);
    display.print("<");

    display.getTextBounds(String(all_mode[(selectedMode + 1) % size]), (width / 3) * 2, 33, &x3, &y1, &w, &h);
    display.setCursor((width - w) - 5, 33);
    display.print(String(all_mode[(selectedMode + 1) % size]));
    display.setCursor((width - w) - 5, 44);
    display.print(">");

    display.getTextBounds(String(all_mode[selectedMode]), 0, 33, &x1, &y1, &w, &h);
    display.setCursor((x3 - x2 - w) / 2 + x2, 33);
    display.print(String(all_mode[selectedMode]));
    display.setCursor((x3 - x2 - (w / 2 - 1)) / 2 + x2, 44);
    display.print("^");
    display.drawLine((x3 - x2 - (w / 2 - 5)) / 2 + x2, 46, (x3 - x2 - (w / 2 - 5)) / 2 + x2, 51, WHITE);

    display.drawRect(0, 30, width, 30, WHITE);
  }
  else if (mode == 1) {
    display.print("\nLuftfeuchtigkeit: " + String(humidity) + "%\nTemperatur: " + String(temperature));
    display.print((char)247);
    display.print("C\nLicht: " + String(light_percentage) + "%");
    display.print("\nHeat-Index: " + String(heatIndex));
    display.print((char)247);
    display.print("C");
  }
  
  display.display();
}

void loop() {
  if (!disabled) {
    humidity = int(dht.readHumidity()); // humidity
    temperature = int(dht.readTemperature()); // temperature
    light = analogRead(PIN_LIGHT_SENSOR); // light
    light_percentage = int((light / 4095) * 100); // light percentage
    voltage = float(analogRead(A0)); // analog voltage - goes from 0-1023 - 1023 is 5V (or 3V if Board is 3V), 0 is 0V  #! Maybe Incorrect, please check if correct
    heatIndex = dht.computeHeatIndex(temperature, humidity, false); // In Celsius

    if (WiFi.status() == WL_CONNECTED) {
      if (!lightDisabled) { digitalWrite(PIN_FUNCTIONAL_LED, HIGH); }
    }
    else {
      connectToWiFi();
    }
  }

  int readingLeft = digitalRead(PIN_LEFT_BUTTON);
  int readingRight = digitalRead(PIN_RIGHT_BUTTON);
  int readingMid = digitalRead(PIN_MID_BUTTON);

  debounce(readingLeft, LEFT, leftButtonState, lastLeftButtonState);
  debounce(readingRight, RIGHT, rightButtonState, lastRightButtonState);
  debounce(readingMid, MID, midButtonState, lastMidButtonState);

  if (!disabled) { updateDisplay(); }
}