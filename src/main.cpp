#include <Arduino.h>
#include <avr/io.h>
#include <avr/interrupt.h>

#define MAGNET_PIN_BIT PD6 
#define SENSOR_PIN_BIT PD3

const uint16_t TIMER_RELOAD = 65285;
const uint8_t SPACING = 10;

volatile uint32_t timer_1ms = 0;
volatile uint16_t jarak = 0;
volatile uint8_t hitung_sensor = 0;
volatile bool flag_start = false;
volatile bool request_print = false;

ISR(TIMER1_OVF_vect) {
    TCNT1 = TIMER_RELOAD;
    timer_1ms++;
}

ISR(INT1_vect) {
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

void setup() {
    // --- CHANGED BAUDRATE HERE ---
    Serial.begin(57600);

    DDRD |= (1 << MAGNET_PIN_BIT);
    PORTD |= (1 << MAGNET_PIN_BIT);

    DDRD &= ~(1 << SENSOR_PIN_BIT);

    cli();

    EICRA |= (1 << ISC11) | (1 << ISC10);
    EIMSK |= (1 << INT1);

    TCCR1A = 0;
    TCCR1B = 0;
    TCNT1 = TIMER_RELOAD;
    TIMSK1 |= (1 << TOIE1);

    sei();
}

void loop() {
    if (Serial.available() > 0) {
        char ds = Serial.read();

        if (ds == 'S' || ds == 's') {
            PORTD &= ~(1 << MAGNET_PIN_BIT);

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
        cli();
        uint16_t cetak_jarak = jarak;
        uint32_t cetak_timer = timer_1ms;
        request_print = false;
        sei();

        Serial.print(cetak_jarak);
        Serial.print(":");
        Serial.print(cetak_timer);
        Serial.println("#");
    }
}