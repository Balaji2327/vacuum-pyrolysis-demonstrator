/*
  Vacuum-Assisted Batch Pyrolysis Demonstrator - reactor temperature logger
  Board : Arduino Uno / Nano (ESP32 works with the same library)
  Sensor: K-type thermocouple + MAX6675
  Lib   : "MAX6675 library" by Adafruit (Library Manager)

  Wiring (MAX6675 -> Arduino): CS->D10, SCK->D13, SO->D12, VCC->5V, GND->GND
  Optional buzzer (monitoring aid only): D8 -> buzzer -> GND, build with -DENABLE_BUZZER

  OUTPUT (9600 baud, CSV):  t_s,temp_c,state
  state = OK | APPROACH | AT_TARGET | OVER_TEMP | FAULT

  SAFETY NOTE: this is MONITORING ONLY. It does not switch the heater and is NOT an
  over-temperature protection system. Heater cut-off stays manual (dimmer/switch/fuse).
*/
#include <max6675.h>

const int PIN_CLK = 13;
const int PIN_CS  = 10;
const int PIN_SO  = 12;
MAX6675 thermocouple(PIN_CLK, PIN_CS, PIN_SO);

const float TARGET_C      = 480.0;   // upper end of the 450-500 C band
const float WARN_MARGIN_C = 20.0;    // "approach" warning window below target
const float OVER_TEMP_C   = 520.0;   // alert threshold above the band
const unsigned long READ_INTERVAL_MS = 1000;  // MAX6675 needs >= 220 ms between reads
const int PIN_BUZZER = 8;

unsigned long lastRead = 0;

void alarm(bool on) {
#ifdef ENABLE_BUZZER
  if (on) tone(PIN_BUZZER, 2000, 200); else noTone(PIN_BUZZER);
#endif
}

void setup() {
  Serial.begin(9600);
#ifdef ENABLE_BUZZER
  pinMode(PIN_BUZZER, OUTPUT);
#endif
  delay(500);  // MAX6675 power-up settle
  Serial.println("# Reactor temperature logger ready");
  Serial.println("# MONITORING ONLY - not an over-temperature protection system");
  Serial.println("t_s,temp_c,state");
}

void loop() {
  unsigned long now = millis();
  if (now - lastRead < READ_INTERVAL_MS) return;
  lastRead = now;

  float tempC = thermocouple.readCelsius();
  float t_s = now / 1000.0;

  if (isnan(tempC)) {
    Serial.print(t_s, 1); Serial.println(",nan,FAULT");
    alarm(true);
    return;
  }

  const char *state = "OK";
  if (tempC >= OVER_TEMP_C)                     state = "OVER_TEMP";
  else if (tempC >= TARGET_C)                   state = "AT_TARGET";
  else if (tempC >= TARGET_C - WARN_MARGIN_C)   state = "APPROACH";

  Serial.print(t_s, 1); Serial.print(",");
  Serial.print(tempC, 1); Serial.print(",");
  Serial.println(state);

  alarm(tempC >= TARGET_C);
}
