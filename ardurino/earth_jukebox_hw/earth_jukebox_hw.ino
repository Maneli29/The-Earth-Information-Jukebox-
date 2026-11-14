#include <Servo.h>
#include <Wire.h>
#include <U8g2lib.h>

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
// U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

Servo needle;

// true  = turning the knob moves the servo and LEDs and shows the level on
//         the screen by itself (standalone hardware test)
// false = only commands from the laptop (Python) drive the outputs
const bool KNOB_DRIVES_OUTPUTS = true;

const int POT_PIN = A0;
const int SERVO_PIN = 9;
const int BUZZER_PIN = 8;
const int BUTTON_PIN = 7;
const int LED_PINS[5] = {2, 3, 4, 5, 6};

char line1[17] = "Earth Jukebox";
char line2[17] = "Ready";
bool screenDirty = true;
unsigned long lastDraw = 0;

char buf[40];
byte bufLen = 0;

int lastPot = -1;
bool lastButton = HIGH;
unsigned long lastSend = 0;

void setLevel(int level) {
  level = constrain(level, 0, 100);
  needle.write(map(level, 0, 100, 0, 180));
  int lit = map(level, 0, 100, 0, 5);
  for (int i = 0; i < 5; i++) digitalWrite(LED_PINS[i], i < lit ? HIGH : LOW);
}

void drawScreen() {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 16, line1);
  u8g2.drawStr(0, 40, line2);
  u8g2.sendBuffer();
}

void handleLine(char *s) {
  if (strncmp(s, "LEVEL,", 6) == 0) {
    setLevel(atoi(s + 6));
  } else if (strncmp(s, "FREQ,", 5) == 0) {
    int f = atoi(s + 5);
    if (f > 0) tone(BUZZER_PIN, f); else noTone(BUZZER_PIN);
  } else if (strncmp(s, "T1,", 3) == 0) {
    strncpy(line1, s + 3, 16); line1[16] = 0; screenDirty = true;
  } else if (strncmp(s, "T2,", 3) == 0) {
    strncpy(line2, s + 3, 16); line2[16] = 0; screenDirty = true;
  }
}

void setup() {
  Serial.begin(9600);
  needle.attach(SERVO_PIN);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  for (int i = 0; i < 5; i++) pinMode(LED_PINS[i], OUTPUT);
  u8g2.begin();
  u8g2.setBusClock(400000);
  setLevel(0);
  drawScreen();
  tone(BUZZER_PIN, 440, 300);   // short startup beep: confirms the buzzer wiring
}

void loop() {
  // 1. Read commands arriving from the laptop, one line at a time
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      buf[bufLen] = 0;
      handleLine(buf);
      bufLen = 0;
    } else if (c != '\r' && bufLen < sizeof(buf) - 1) {
      buf[bufLen++] = c;
    }
  }

  // 2. Redraw the screen only when the text changed
  if (screenDirty && millis() - lastDraw > 150) {
    drawScreen();
    screenDirty = false;
    lastDraw = millis();
  }

  // 3. Report the knob position to the laptop (and optionally drive outputs)
  if (millis() - lastSend > 50) {
    lastSend = millis();
    int pot = analogRead(POT_PIN);
    if (abs(pot - lastPot) > 3) {
      Serial.print("POT,");
      Serial.println(pot);
      lastPot = pot;
      if (KNOB_DRIVES_OUTPUTS) {
        int lv = map(pot, 0, 1023, 0, 100);
        setLevel(lv);
        snprintf(line2, sizeof(line2), "Level %d", lv);
        screenDirty = true;
      }
    }
  }

  // 4. Report button presses
  bool b = digitalRead(BUTTON_PIN);
  if (lastButton == HIGH && b == LOW) {
    Serial.println("BTN");
    delay(30);
  }
  lastButton = b;
}