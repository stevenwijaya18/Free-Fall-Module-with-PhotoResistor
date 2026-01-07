#include <Arduino.h>

#define MAGNET_PIN 6
#define SENSOR_PIN 3

const uint16_t TIMER_RELOAD = 65285;
const uint8_t SPACING = 10;

volatile uint32_t timer_1ms = 0;
volatile uint16_t jarak = 0;
volatile uint8_t hitung_sensor = 0;
volatile bool flag_start = false;
volatile bool request_print = false;

void isr_sensor();

void setup() {
  Serial.begin(115200);
  
  pinMode(MAGNET_PIN, OUTPUT);
  digitalWrite(MAGNET_PIN, HIGH);
  
  pinMode(SENSOR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), isr_sensor, RISING);

  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = TIMER_RELOAD;
  TIMSK1 |= (1 << TOIE1);
  interrupts();
}

void loop() {
  if (Serial.available() > 0) {
    char ds = Serial.read();
    
    if (ds == 'S' || ds == 's') {
      digitalWrite(MAGNET_PIN, LOW);
      
      TCCR1B = 0;
      TCNT1 = TIMER_RELOAD;
      
      timer_1ms = 0;
      jarak = 0;
      hitung_sensor = 0;
      flag_start = true;
      
      Serial.print(jarak);
      Serial.print(":");
      Serial.print(timer_1ms);
      Serial.println("#");
      
      TCCR1B |= (1 << CS11) | (1 << CS10);
    }
  }

  if (request_print) {
    noInterrupts();
    uint16_t current_jarak = jarak;
    uint32_t current_timer = timer_1ms;
    request_print = false;
    interrupts();

    Serial.print(current_jarak);
    Serial.print(":");
    Serial.print(current_timer);
    Serial.println("#");
  }
}

ISR(TIMER1_OVF_vect) {
  TCNT1 = TIMER_RELOAD;
  timer_1ms++;
}

void isr_sensor() {
  if (flag_start) {
    hitung_sensor++;
    
    if (hitung_sensor <= 10) {
      jarak += SPACING;
      request_print = true;
      
      if (hitung_sensor == 10) {
        TCCR1B &= ~((1 << CS12) | (1 << CS11) | (1 << CS10));
        flag_start = false;
      }
    }
  }
}
