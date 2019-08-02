#define MA_1 10
#define MA_2 9
#define MA_PWM 6
#define MB_1 8
#define MB_2 7
#define MB_PWM 5

#define OPEN 0
#define CLOSE 1
#define STOP 2

#define fastArm false
#define slowArm true

#define potEnable 13
#define slowArmPin A1
#define fastArmPin A2

#define fastArmLimit 180
#define slowArmLimit 885

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(potEnable, OUTPUT);

  //enable readout from potentiometer
  digitalWrite(potEnable, HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:

  Serial.println(armPos_raw(slowArm));
  arm_to_base(slowArm);
  delay(999999999);
}

int currpos(bool whichArm) {
  return (int)armPos_raw(whichArm) * (100/1024);
}

void arm_to_base(bool whichArm) {

  motor(whichArm, OPEN, 100);

  if(whichArm == fastArm) {
    while(armPos_raw(whichArm) > fastArmLimit) {}
  }
  else {
    while(armPos_raw(whichArm) < slowArmLimit) {}
  }
  motor(whichArm, STOP, 0);
}


int armPos_raw(bool whichArm){
  if(whichArm == slowArm) {
    return analogRead(slowArmPin);
  }
  else {
    return analogRead(fastArmPin);
  }
}


void motor(bool motor_select, int dir, float percentage_power) {

    int power = (int)percentage_power*255/100;

    if(motor_select == slowArm) {
          if(dir == STOP) {
            digitalWrite(MA_1, LOW); digitalWrite(MA_2, LOW); analogWrite(MA_PWM, 0);
          }
          else{
            if(dir==OPEN){
              digitalWrite(MA_1, HIGH); digitalWrite(MA_2, LOW); analogWrite(MA_PWM, power);
            }
            else{
              digitalWrite(MA_1, LOW); digitalWrite(MA_2, HIGH); analogWrite(MA_PWM, power);
            }
          }
    }
    else {
          if(dir == STOP) {
            digitalWrite(MB_1, LOW); digitalWrite(MB_2, LOW); analogWrite(MB_PWM, 0);
          }
          else{
            if(dir==CLOSE){
              digitalWrite(MB_1, HIGH); digitalWrite(MB_2, LOW); analogWrite(MB_PWM, power);
            }
            else{
              digitalWrite(MB_1, LOW); digitalWrite(MB_2, HIGH); analogWrite(MB_PWM, power);
            }
          }
    }
}
