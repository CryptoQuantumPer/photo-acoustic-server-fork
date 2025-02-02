#include <Servo.h>
Servo servo_x_axis;
Servo servo_y_axis;
#define laser_relay_pin 5
#define servo_x_axis_pin 9
#define servo_y_axis_pin 10
#define hantek_sig_pin 6
#define limit_switch 3
#define photo_diode_a 0
float pos_x = 0;  //home
float pos_y = 0;
int laser_operation_frq = 1;
int n_commands = 14;


float forward_90_per_second = 55.90;
float backward_90_per_second = 123.10;

/*
servo settings
  55.90 123.10
  64 115
  50 130
*/






void setup() {
  Serial.begin(115600);
  Serial.setTimeout(1);

  pinMode(hantek_sig_pin, OUTPUT);
  pinMode(laser_relay_pin, OUTPUT);
  pinMode(servo_x_axis_pin, OUTPUT);
  pinMode(servo_y_axis_pin, OUTPUT);
  pinMode(limit_switch, INPUT);
  pinMode(3, INPUT);
}




String msg;
const String commands[14] = { "FIREL0", "FIREL1", "LED_BUILTIN1", "LED_BUILTIN0", "MOVE", "HOME",
                           "1000", "FIREL000", "SET_FRQ", "SPEEDBACK", "SPEEDFOR", "GETSPEED", "CALIBRATION", "XHOME"};





void zero_x(){
  int x_initial_position = 0; // go back to home
  while (analogRead(limit_switch) != 0) {
    move_position(x_initial_position, pos_y);
    x_initial_position--; 
  }
  pos_x = 0;
}

int _optimal_(int offset, float alpha = 0.3){
  float rate_summation = offset * alpha;
  return rate_summation;
}

void find_optimal_value(float forward_start , float backward_start, int steps_bf_turn = 10, float alpha = 0.3){
  
  zero_x();
  forward_90_per_second = forward_start;
  backward_90_per_second = backward_start;

  int offset = 0;
  for(int x = 0; x < steps_bf_turn; x++){ // go to steps_bf_turn "backward"
    move_position(x, 0);
  }

  int x = steps_bf_turn;
  while(analogRead(limit_switch) != 0) {
    move_position(x, 0);
    x--;
  }
  offset = x * -1; //if + means go slower; - go faster

  float rate_summation = _optimal_(offset);
  forward_90_per_second = forward_90_per_second + rate_summation;
  backward_90_per_second = backward_90_per_second + rate_summation;
  Serial.print("SET new forward and backward value to >>"); Serial.print(forward_90_per_second); Serial.print(" "); Serial.println(backward_90_per_second); 
  Serial.print("OffSet >> "); Serial.print(offset); Serial.print(" changes to val: ");Serial.println(rate_summation);
}









void loop() {
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
          Serial.print("moving to "); Serial.print(msg_split[1].toInt()); Serial.print(" "); Serial.println(msg_split[2].toInt());
          move_position(msg_split[1].toInt(), msg_split[2].toInt());
          // Serial.println("MOVED TO POSITION");
        }
        else if (msg == commands[5]){ // home
          SETHOME();
        }
        // 1000 DURATION_UNTIL_RETURN  SPEED // test for servo rotation rate
        else if (msg_split[0] == commands[6]){ 
          Serial.println("MOVE 1000ms");
          int speed = msg_split[2].toInt();
          int reverse_speed = (90-speed) + 90;
          servo_x_axis.attach(servo_x_axis_pin);
          servo_x_axis.write(speed);
          delay(1000);
          servo_x_axis.write(90);
          delay(msg_split[1].toInt());

          servo_x_axis.write(reverse_speed);
          delay(1000);
          servo_x_axis.write(90);
          servo_x_axis.detach();
        }
        

        else if (msg_split[0] == commands[7]){
          int fire_cycles = msg_split[1].toInt();
          Serial.print("FIRE "); Serial.print(fire_cycles); Serial.println(" times");
          activate_laser(HIGH);

          for (int i = 0; i < fire_cycles; i++){
            while (analogRead(photo_diode_a) < 1000){} // delay

          }
          activate_laser(LOW);
        }

        //settings for new laser operating frequency
        else if (msg_split[0] == commands[8]){
          laser_operation_frq = msg_split[1].toInt();
          Serial.print("SET new frequency >> "); Serial.print(laser_operation_frq); Serial.print(" hz"); Serial.println();
        }

        else if(msg_split[0] == commands[9]){
          backward_90_per_second = msg_split[1].toInt();
          Serial.print("set backward speed "); Serial.println(msg_split[1].toInt());
        }
        
        else if (msg_split[0] == commands[10]){
          forward_90_per_second = msg_split[1].toInt();
          Serial.print("set forward speed "); Serial.println(msg_split[1].toInt());
        }

        else if(msg == commands[11]){
          Serial.print("forward_90_per "); Serial.print(forward_90_per_second); Serial.print("; backward_90_per_second "); Serial.print(backward_90_per_second); Serial.println();
        }

        else if(msg_split[0] == commands[12]){
          while(true){
            Serial.print("forward_90_per "); Serial.print(forward_90_per_second); Serial.print("; backward_90_per_second "); Serial.print(backward_90_per_second); Serial.println();
            find_optimal_value(forward_90_per_second, backward_90_per_second, 10);
          }
        }


        else if(msg == commands[13]){
          zero_x();
        }


        else { 
          Serial.println(""); 
          Serial.write("invalid input");
          printCommands();
          }
  }


  // --------PERIPERIAL OPERATION---------
  int photo_readout = analogRead(photo_diode_a);
  while (photo_readout >= 1000){
        Serial.print("PEAK ");Serial.println(photo_readout);
        photo_readout = analogRead(photo_diode_a);
        digitalWrite(hantek_sig_pin, HIGH);
        delay(100);
  }
  digitalWrite(hantek_sig_pin, LOW);


}




const float gear_dia = 7;
const float circumference = 3.1415926 * gear_dia * 2;

void move_position(float x, float y) {
  if (analogRead(limit_switch) != 0 || x >= pos_x){  // run only while not limit
      servo_x_axis.attach(servo_x_axis_pin);
      servo_y_axis.attach(servo_y_axis_pin);

      float diviation_x_axis = abs(x - pos_x);  // mm
      float diviation_y_axis = abs(y - pos_y);  // mm
      float x_deg_req = (diviation_x_axis / circumference) * 360;
      float y_deg_req = (diviation_y_axis / circumference) * 360;
      float x_time = (x_deg_req / 90) * 1000;
      float y_time = (y_deg_req / 90) * 1000;

      
      
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
      // Serial.print("x position "); Serial.print(pos_x); Serial.print(" y position "); Serial.println(pos_y);
      servo_x_axis.detach();
      servo_y_axis.detach();
  } 
  else{
    Serial.println("LIMIT");
  }
  pos_x = x; // update current position
  pos_y = y;
  
}


void SETHOME(){
  pos_x = 0; pos_y = 0;
  Serial.println("SETHOME");
}


void printCommands() {
    Serial.println("Available Commands:");
    for (int i = 0; i < n_commands; i++) {
        Serial.print(i);
        Serial.print(": ");
        Serial.println(commands[i]);
    }
}

void activate_laser(int activation) {
  digitalWrite(laser_relay_pin, activation);
  if (activation == LOW) {
    Serial.println("L_off");
  } else if (activation == HIGH) {
    Serial.println("L_on");
  }
}




