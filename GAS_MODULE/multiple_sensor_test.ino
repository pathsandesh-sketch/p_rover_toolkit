const int SENSOR_PIN1 = A0; 
const int SENSOR_PIN2 = A1; 
const int SENSOR_PIN3 = A2; 


void setup() {
  Serial.begin(9600);
  Serial.println("====================================");
  Serial.println("Testing Multiple Sensors");
  Serial.println("====================================");
}

void loop() {
  int rawValue1 = analogRead(SENSOR_PIN1);
  int rawValue2 = analogRead(SENSOR_PIN2);
  int rawValue3 = analogRead(SENSOR_PIN3);

  float voltage = rawValue1 * (5.0 / 1023.0);

  Serial.print("CO  Raw Value: "); //MQ-7
  Serial.print(rawValue1);
  Serial.print("   |   H2S Raw Value: ");//MQ-135
  Serial.print(rawValue2);
  Serial.print("   |   CH4 Raw Value: ");//MQ-4
  Serial.print(rawValue3);


  Serial.print("   |   Voltage: ");
  Serial.print(voltage);
  Serial.println("V");

  delay(1000); // Read every second
}
