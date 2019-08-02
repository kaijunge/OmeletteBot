bool task = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("Ready");
  
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  
  
  pinMode(11, OUTPUT);
  pinMode(12, INPUT);
  digitalWrite(11, HIGH);
}

void loop() {
  open_gripper();
  digitalWrite(8, LOW); digitalWrite(9, LOW); analogWrite(10, 0);

  while(true){    
    if(Serial.read() == 49){ break; }
  }
  Serial.println("ACTIVATED");
  Serial.println("10");


  while(true){
    char bytein = Serial.read();
    
    
    if(bytein == '2')
    {
      close_whisk();
      Serial.println("5");
    }
    
    else if(bytein == '3')
    {
      close_bowl();
      Serial.println("5");  
    }
    else if(bytein == '4')
    {
      open_a_bit();
      Serial.println("5");
    }
    else if(bytein == '6')
    {
      open_gripper();
      Serial.println("5");
    }
    else if(bytein == '7')
    {
      close_a_bit();
      Serial.println("5");
    }
    else if(bytein == '8')
    {
      close_pan();
      Serial.println("5");
    }
  }
}

void close_whisk() {
  digitalWrite(8, LOW); digitalWrite(9, HIGH); analogWrite(10, 255);
  delay(5000);

  digitalWrite(8, LOW); digitalWrite(9, HIGH); analogWrite(10, 60);
  delay(1000);
  digitalWrite(8, LOW); digitalWrite(9, HIGH); analogWrite(10, 20);
  delay(3000);
  digitalWrite(8, LOW); digitalWrite(9, LOW); analogWrite(10, 0);
}

void close_bowl() {
  digitalWrite(8, LOW); digitalWrite(9, HIGH); analogWrite(10, 255);
  delay(9000);

  digitalWrite(8 , LOW); digitalWrite(9, HIGH); analogWrite(10, 25);
  delay(4000);

  digitalWrite(8, LOW); digitalWrite(9, LOW); analogWrite(10, 0);
}

void open_gripper() {
  digitalWrite(8, HIGH); digitalWrite(9, LOW); analogWrite(10, 255);
  while(digitalRead(12) == 0) {}
  digitalWrite(8, LOW); digitalWrite(9, LOW); analogWrite(10, 0);
}

void open_a_bit(){
  digitalWrite(8, HIGH); digitalWrite(9, LOW); analogWrite(10, 255);
  delay(600);
  digitalWrite(8, LOW); digitalWrite(9, LOW); analogWrite(10, 0);
}

void close_a_bit(){
  digitalWrite(8, LOW); digitalWrite(9, HIGH); analogWrite(10, 50);
  delay(500);
  digitalWrite(8, LOW); digitalWrite(9, LOW); analogWrite(10, 0);
}

void close_pan(){
  digitalWrite(8, LOW); digitalWrite(9, HIGH); analogWrite(10, 255);
  delay(5500);

  digitalWrite(8 , LOW); digitalWrite(9, HIGH); analogWrite(10, 25);
  delay(2000);

  digitalWrite(8, LOW); digitalWrite(9, LOW); analogWrite(10, 0);
}
