void setup() {
  Serial.begin(115600);
  Serial.setTimeout(1);
}

String InBytes;

void loop() {

  // serial communication
  if (Serial.available() > 0) {
    InBytes = Serial.readStringUntil('\n');
    if (InBytes == "on") {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.write("LED on");
    }
    else if (InBytes == "off") {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.write("Led off");
    }
    else {
      Serial.write("invalid input");
    }
  }
}
