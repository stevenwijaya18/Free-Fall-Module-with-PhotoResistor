#include <Arduino.h>

const int SENSOR_PIN = 2;
const long BAUD_RATE = 115200;
const int MAX_DATA = 100;

volatile unsigned long timestamps[MAX_DATA];
volatile int head = 0;
int tail = 0;

void sensorISR();

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(SENSOR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), sensorISR, RISING);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'R' || cmd == 'r') {
      noInterrupts();
      head = 0;
      tail = 0;
      interrupts();
    }
  }

  if (head != tail) {
    noInterrupts();
    unsigned long timeToSend = timestamps[tail];
    interrupts();
    
    Serial.println(timeToSend);
    tail = (tail + 1) % MAX_DATA;
  }
}

void sensorISR() {
  timestamps[head] = micros();
  head = (head + 1) % MAX_DATA;
}