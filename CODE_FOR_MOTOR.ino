#include <Servo.h>

Servo myServo;

void setup() {
  Serial.begin(9600);
  myServo.attach(9);
}

// when less then 92 it goes counter clockwise

void loop() {
  myServo.write(90);
  if (Serial.available() > 0) {
    char input = Serial.read();

    if (input == 'R') {
      myServo.write(94);  
      delay(900);         
      myServo.write(90);  
      delay(900);
      myServo.write(92);
    } 
    else if (input == 'T') {
      myServo.write(90);  
      delay(900);         
      myServo.write(94);  
      delay(900);
      myServo.write(90);
    }
    else if (input == 'U') {
      myServo.write(92);  // STOEEEEEEEEFC
    }
  }
}

