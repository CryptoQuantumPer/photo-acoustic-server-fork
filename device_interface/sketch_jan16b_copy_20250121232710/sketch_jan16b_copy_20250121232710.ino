#include <Servo.h>
Servo servo_x_axis;
Servo servo_y_axis;
int laser_relay_pin = 5;
int servo_x_axis_pin = 9;
int servo_y_axis_pin = 10;
float pos_x = 0;  //home
float pos_y = 0;
#define forward_90_per_second 40
#define backward_90_per_second 140

/*
servo settings
42 for 90+/sec
120 for 90-/sec
void move90degress(range_mm){
    servo.move(90) center
    servo.move
}
*/


void setup() {
  Serial.begin(115600);
  Serial.setTimeout(1);

  pinMode(laser_relay_pin, OUTPUT);
  pinMode(servo_x_axis_pin, OUTPUT);
  pinMode(servo_y_axis_pin, OUTPUT);
}



void activate_laser(int activation) {
  digitalWrite(laser_relay_pin, activation);
  if (activation == LOW) {
    Serial.println("L_off");
  } else if (activation == HIGH) {
    Serial.println("L_on");
  }
}







String msg;
const String commands[6] = { "FIREL0", "FIREL1", "LED_BUILTIN1", "LED_BUILTIN0", "MOVE", "HOME" };


void loop() {
  // digitalWrite(5, HIGH);
  // delay(1000);
  // digitalWrite(5, LOW);
  // delay(1000);


  while (Serial.available()) {

    msg = Serial.readStringUntil('\n');

    //------split msg---------
    String msg_split[3];
    int i = 0;
    int token_start = 0;
    int token_end = msg.indexOf(' ');
    while (token_end != -1) {
      msg_split[i++] = msg.substring(token_start, token_end);
      token_start = token_end + 1;
      token_end = msg.indexOf(' ', token_start);
    }
    msg_split[i] = msg.substring(token_start);

    //--------run functions------------
    if (msg == commands[0]) {
      activate_laser(LOW);
    } 
    else if (msg == commands[1]) {
      activate_laser(HIGH);
    } 
    else if (msg == commands[2]) { // LED_on
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED_BUILTIN_on");
    } 
    else if (msg == commands[3]) { // LED_off
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("LED_BUILTIN_off");
    } 
    else if (msg_split[0] == commands[4]){ // MOVE Gantry
      move_position(msg_split[1].toFloat(), msg_split[2].toFloat());
      Serial.println("MOVED TO POSITION");
    }
    else if (msg == commands[5]){ // home
      pos_x = 0; pos_y = 0;
      Serial.println("SETHOME");
    }


    else { Serial.println(""); Serial.write("invalid input"); }
  }

  // --------periperal operations---------
  int photo_readout = analogRead(0);
  if (photo_readout >= 1000){
    Serial.print("photo peak detected ");Serial.println(photo_readout);
  }
}








const float gear_dia = 7;
const float circumference = 3.1415926 * gear_dia * 2;

void move_position(float x, float y) {
  servo_x_axis.attach(servo_x_axis_pin);
  servo_y_axis.attach(servo_y_axis_pin);
  // translate to seconds

  float diviation_x_axis = abs(x - pos_x);  // mm
  float diviation_y_axis = abs(y - pos_y);  // mm



  // convert 90*/sec to mm/sec
  // time = (deg_req / rate_of_rotation) * 1000 (convert to ms)
  float x_deg_req = (diviation_x_axis / circumference) * 360;
  float y_deg_req = (diviation_y_axis / circumference) * 360;
  float x_time = (x_deg_req / 90) * 1000;
  float y_time = (y_deg_req / 90) * 1000;

  // response
  if (diviation_x_axis != 0 || diviation_y_axis != 0){
    Serial.write("diviation"); Serial.write(" ");Serial.write(diviation_x_axis); Serial.write(" "); Serial.write(diviation_y_axis); Serial.println();
  }
  if (x_time != 0 || y_time != 0){
    Serial.print("time: "); Serial.print(x_time); Serial.print(" "); Serial.println(y_time);
  }

  if (x < pos_x) {
    servo_x_axis.write(forward_90_per_second);
    delay(x_time);
    servo_x_axis.write(90);  //stop
  } else if (x > pos_x) {
    servo_x_axis.write(backward_90_per_second);
    delay(x_time);
    servo_x_axis.write(90);
  }

  if (y < pos_y) {
    servo_y_axis.write(forward_90_per_second);
    delay(y_time);
    servo_y_axis.write(90);  //stop
  } else if (y > pos_y) {
    servo_y_axis.write(backward_90_per_second);
    delay(y_time);
    servo_y_axis.write(90);
  }


  // update current position
  pos_x = x;
  pos_y = y;
  Serial.print(pos_x); Serial.println(pos_y); // print current position
  servo_x_axis.detach();
  servo_y_axis.detach();
}

