#include <Arduino.h>

// --- KONFIGURASI ---
const int SENSOR_PIN = 2;
const long BAUD_RATE = 115200;
const int MAX_DATA = 100;

// --- VARIABEL ---
volatile unsigned long timestamps[MAX_DATA];
volatile int head = 0;
int tail = 0;

// --- FUNCTION PROTOTYPE ---
// Baris ini WAJIB ada di PlatformIO untuk mencegah error "not declared in this scope"
void sensorISR(); 

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(SENSOR_PIN, INPUT);
  
  // Menggunakan fungsi 'sensorISR' yang sudah dideklarasikan di atas
  attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), sensorISR, RISING);
}

void loop() {
  // Cek perintah reset dari Python
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'R' || cmd == 'r') {
      noInterrupts();
      head = 0;
      tail = 0;
      interrupts();
    }
  }

  // Kirim data jika ada antrian
  if (head != tail) {
    noInterrupts();
    unsigned long timeToSend = timestamps[tail];
    interrupts();
    
    Serial.println(timeToSend);
    tail = (tail + 1) % MAX_DATA;
  }
}

// --- FUNGSI INTERRUPT ---
void sensorISR() {
  timestamps[head] = micros();
  head = (head + 1) % MAX_DATA;
}