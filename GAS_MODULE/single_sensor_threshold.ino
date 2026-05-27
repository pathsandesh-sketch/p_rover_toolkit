const int SENSOR_PIN = A0;

// Change this number based on your sensor's stable clean-air reading
const int GAS_THRESHOLD = 450; 

void setup() {
  Serial.begin(9600);
  Serial.println("====================================");
  Serial.println("Testing MQ-135 with Alert Logic     ");
  Serial.println("====================================");
}

void loop() {
  int rawValue = analogRead(SENSOR_PIN);
  float voltage = rawValue * (5.0 / 1023.0);

  // Print the data stream
  Serial.print("Raw Value: ");
  Serial.print(rawValue);
  Serial.print("   |   ");

  // --- IF/ELSE LOGIC START ---
  if (rawValue > GAS_THRESHOLD) {
    Serial.println("ALERT: Gas Detected! Above Baseline!");
  } else {
    Serial.println("Air Status: Clean (Normal Baseline)");
  }

  delay(1000); 
}
