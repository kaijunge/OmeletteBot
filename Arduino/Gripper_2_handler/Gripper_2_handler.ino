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

#define potEnable 12
#define slowArmPin A1
#define fastArmPin A2

#define fastArmLimit 180
#define slowArmLimit 880
#define closingLimit 165 //165

#define potTolerance 13

bool fastArmStatus = false;
bool slowArmStatus = false;

#define ARMS_TOGETHER 3

/*
------------- Gripper manipulation cases --------------
*/

#define restart '0'
#define normalGrip '1'
#define mediumGrip '2'
#define hardGrip '3'
#define openMM '4'
#define closeMM '5'
#define gripInCentre '6'
#define openGripper '7'
#define lightGrip '8'
#define fastArmOnlyGrip '9'


bool debug = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  // Set pinmodes
  pinMode(potEnable, OUTPUT);

  //enable readout from potentiometer
  digitalWrite(potEnable, HIGH);

  // if debug mode or not
  debug = false;
}

void loop() {
  // begin main loop
  while(true) {
    //printArmPos();
  
    char readIn = Serial.read();
  
    if(readIn == restart) {
      Serial.print("RESTARRING");
      initArms();
    }
    else if(readIn == normalGrip) {
      Serial.print("NORMAL GRIP");
      gripObjects(2, 70);
    }
    else if(readIn == mediumGrip) {
      Serial.print("MEDIUM GRIP");
      gripObjects(2, 97);
    }
    else if(readIn == hardGrip) {
      Serial.print("HARD GRIP");
      gripObjects(2, 120);
    }
    else if(readIn == openMM) {
      
      gripObjects(2, 85);
    }
    else if(readIn == closeMM) {
      
    }
    else if(readIn == gripInCentre) {
      
    }
    else if(readIn == openGripper) {
      both_arms_to_base();
    }
    else if(readIn == lightGrip) {
      
    }
    else if(readIn == fastArmOnlyGrip) {
      gripObjects(0, 0);
    }
    
  }
  
}

void gripObjects(int mode, int currentThreshold) {
  long timer;
  switch(mode) {
    case 0:
      if(debug) { Serial.print("Gripping Objects, Fast Arm: "); Serial.println(mode); }
      
      moveArm(fastArm, CLOSE, 100);
      delay(100);
      timer = millis();
      while((readCurrent() > 20 || readCurrent() < 5) && errorCheck() == 0 && millis() - timer < 100) {}

      while(true) {
        if(readCurrent() > 55) {
          // Current detected
          Serial.println("Complete");
          break;
        }

        if(errorCheck() != 0) {
          Serial.println("Error Detected");
          break;
        }
      }

      moveArm(fastArm, STOP, 0);

      break;
    case 1:

      break;
    case 2:
      if(debug) { Serial.print("Gripping Objects, Both Arms: "); Serial.println(mode);}
      
      moveArm(fastArm, CLOSE, 100);
      moveArm(slowArm, CLOSE, 100);
      delay(200);
      timer = millis();
      while((readCurrent() > 50 || readCurrent() < 5) && errorCheck() == 0 && millis() - timer < 250) {}

      while(true) {

        if(debug) { Serial.println(readCurrent()); }
        printArmPos();
        
        if(readCurrent() > currentThreshold) {
          Serial.println("Complete");
          break;
        }

        if(errorCheck() != 0) {
          Serial.println("Error");
          Serial.println(errorCheck());
          break;
        }
      }

      moveArm(fastArm, STOP, 0);
      moveArm(slowArm, STOP, 0);
      break;
    case 3:
    // move to certain position
    
      break;
      
    default:
      Serial.println("No gripping style specifified");
      break;
  }
  
}

void initArms() {
  if(debug) { Serial.println("Initiating Arms"); }
  
  both_arms_to_base();


// UNNEEDED MOVEMENTS
/*
  if(errorCheck() == 0) {
      Serial.println("Assuming both arms at base!");
      moveArm(slowArm, CLOSE, 100);
      moveArm(fastArm, CLOSE, 100);
      delay(500);
    
      moveArm(slowArm, OPEN, 100);
      moveArm(fastArm, OPEN, 100);
    
      while(fastArmStatus == true || slowArmStatus == true) {
        if(armPos_raw(fastArm) < fastArmLimit) {
          moveArm(fastArm, STOP, 0);
        }
        
        if(armPos_raw(slowArm) > slowArmLimit) {
          moveArm(slowArm, STOP, 0);
        } 
      }
  }
  */

  if(debug) {
    Serial.print("Error Code:  "); Serial.println(errorCheck());
    Serial.print("Fast arm:  "); Serial.println(armPos_raw(fastArm));
    Serial.print("Slow arm:  "); Serial.println(armPos_raw(slowArm));
    Serial.println("Initiation Complete\n\n");
  }
}

float readCurrent() {
  return analogRead(A0);
}

int currpos(bool whichArm) {
  return (int)armPos_raw(whichArm) * (100/1024);
}

void arm_to_base(bool whichArm) {

  moveArm(whichArm, OPEN, 100);

  if(whichArm == fastArm) {
    while(armPos_raw(whichArm) > fastArmLimit + potTolerance) {}
  }
  else {
    while(armPos_raw(whichArm) < slowArmLimit - potTolerance) {}
  }
  moveArm(whichArm, STOP, 0);
}

void both_arms_to_base() {

  if(errorCheck_Harsh() == ARMS_TOGETHER) {

    bool whichArm;
    if(abs(armPos_raw(slowArm) - slowArmLimit) > abs(armPos_raw(fastArm) - fastArmLimit)) {
      whichArm = slowArm;
    }
    else {
      whichArm = fastArm; 
    }

    moveArm(whichArm, OPEN, 100);
    Serial.println("HERE!");
    delay(500);
  }
  
  moveArm(slowArm, OPEN, 100);
  moveArm(fastArm, OPEN, 100);

  while(fastArmStatus == true || slowArmStatus == true) {

    if(armPos_raw(fastArm) < fastArmLimit + potTolerance) {
      moveArm(fastArm, STOP, 0);
    }
    
    if(armPos_raw(slowArm) > slowArmLimit - potTolerance) {
      moveArm(slowArm, STOP, 0);
    }

    if(errorCheck() != 0) {
      moveArm(fastArm, STOP, 0);
      moveArm(slowArm, STOP, 0);

      if(debug) {
        Serial.print("ERROR OCCURED CHECK SYSTEM!!    Error: ");
        Serial.println(errorCheck());
      }
      else {
        Serial.println("Error");
        Serial.println(errorCheck());
      }
    }  
  }

  if(errorCheck() == 0) {
    Serial.println("Both arms back to base");
    Serial.println("Complete");
  }
 
}

void printArmPos() {
  Serial.print("Arm positions:  Slow Arm : "); Serial.print(armPos_raw(slowArm)); Serial.print("  Fast Arm : "); Serial.println(armPos_raw(fastArm));
}

int armPos_raw(bool whichArm){
  if(whichArm == slowArm) {
    return analogRead(slowArmPin);
  }
  else {
    return analogRead(fastArmPin);
  }
}

int errorCheck() {
  int error = 0;
  
  // IF ARM IS BEYOND THEIR LIMITS
  if(armPos_raw(fastArm) < fastArmLimit - potTolerance) {
     error = 1;
  }

  if(armPos_raw(slowArm) > slowArmLimit + potTolerance) {
    error = 2;
  }
  
  // IF ARMS ARE COLLIDING TO EACH OTHER
  if(armPos_raw(slowArm) - armPos_raw(fastArm) < closingLimit) {
    error = 3;
  }

  return error;
}

int errorCheck_Harsh() {
  int error = 0;
  
  // IF ARM IS BEYOND THEIR LIMITS
  if(armPos_raw(fastArm) < fastArmLimit - potTolerance*2) {
     error = 1;
  }

  if(armPos_raw(slowArm) > slowArmLimit + potTolerance*2) {
    error = 2;
  }
  
  // IF ARMS ARE COLLIDING TO EACH OTHER
  if(armPos_raw(slowArm) - armPos_raw(fastArm) < closingLimit + 50) {
    error = 3;
  }

  return error;
}

int currentSense() {
  return 0;
}


void moveArm(bool whichArm, int dir, float percentage_power) {

    int power = (int)percentage_power*255/100;

    if(whichArm == slowArm) {
          if(dir == STOP) {
            digitalWrite(MA_1, LOW); digitalWrite(MA_2, LOW); analogWrite(MA_PWM, 0);
            slowArmStatus = false;
          }
          else{
            if(dir==OPEN){
              digitalWrite(MA_1, HIGH); digitalWrite(MA_2, LOW); analogWrite(MA_PWM, power);
            }
            else{
              digitalWrite(MA_1, LOW); digitalWrite(MA_2, HIGH); analogWrite(MA_PWM, power);
            }
            slowArmStatus = true;

          }
    }
    else {
          if(dir == STOP) {
            digitalWrite(MB_1, LOW); digitalWrite(MB_2, LOW); analogWrite(MB_PWM, 0);
            fastArmStatus = false;
          }
          else{
            if(dir==CLOSE){
              digitalWrite(MB_1, HIGH); digitalWrite(MB_2, LOW); analogWrite(MB_PWM, power);
            }
            else{
              digitalWrite(MB_1, LOW); digitalWrite(MB_2, HIGH); analogWrite(MB_PWM, power);
            }
            fastArmStatus = true;
          }
    }

    //Serial.print(fastArmStatus); Serial.println(slowArmStatus);
}
