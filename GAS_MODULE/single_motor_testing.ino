const int SENSOR_PIN = A0; // Look at Analog Pin 0

void setup() {
  Serial.begin(9600);
  Serial.println("====================================");
  Serial.println("Testing Sensor 1: MQ-135 (Air Quality)");
  Serial.println("====================================");
}

void loop() {
  int rawValue = analogRead(SENSOR_PIN);
  float voltage = rawValue * (5.0 / 1023.0);

  Serial.print("MQ-135 Raw Value: ");
  Serial.print(rawValue);
  Serial.print("   |   Voltage: ");
  Serial.print(voltage);
  Serial.println("V");

  delay(1000); // Read every second
}
