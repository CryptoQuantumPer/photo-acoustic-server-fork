#include <servo.h>
int laser_relay_pin = 8;

/*
servo settings

42 for 90+/sec
120 for 90-/sec

void move90degress(range_mm){
    servo.move(90) center
    servo.move

}
*/

void setup(){
    Serial.begin(115600);

}

string msg = "";
const string commands[2] = {"FIRE_LH", "FIRE_LL"};

void loop(){
    while (Serial.avaliable()){
        msg = Serial.readString();
        if (msg == commands[0]){ activate_laser(HIGH);}
        if (msg == commands[1]){ activate_laser(LOW); }
        
        // run functin if msg is activated
    }


}

void activate_laser(int activation){
    digitalWrite(laser_relay_pin, activation);
    if (activation == LOW){
        Serial.println("L_off");
    }
    else if (activation == HIGH){
        Serial.println("L_on");
    }
}

// home
float x = 0;
float y = 0;
#define forward_90_per_second 45
#define backward_90_per_second 125

void move_position(float x, float y){
    servo.attach(9)
    servo.attach(8)
    // translate to seconds

    servo.detach()

}