
#include <AccelStepper.h>

#define MOTOR1_DIR 12
#define MOTOR1_STEP 13

#define MOTOR2_DIR 27
#define MOTOR2_STEP 14


#define MOTOR3_DIR 25
#define MOTOR3_STEP 26


#define MOTOR4_DIR 32
#define MOTOR4_STEP 33

#define MOTOR5_DIR 4
#define MOTOR5_STEP 15

#define MOTOR6_DIR 21
#define MOTOR6_STEP 19


#define MOTOR7_DIR 18
#define MOTOR7_STEP 5

#define MOTOR1_MAXSPEED 6000
#define MOTOR2_MAXSPEED 6000
#define MOTOR3_MAXSPEED 6000
#define MOTOR4_MAXSPEED 6000
#define MOTOR5_MAXSPEED 6000
#define MOTOR6_MAXSPEED 6000
#define MOTOR7_MAXSPEED 3000

#define MOTOR1_MAXACCEL 3000
#define MOTOR2_MAXACCEL 3000
#define MOTOR3_MAXACCEL 3000
#define MOTOR4_MAXACCEL 3000
#define MOTOR5_MAXACCEL 3000
#define MOTOR6_MAXACCEL 3000
#define MOTOR7_MAXACCEL 3000

#define JOINT2_DEFAULT 55
#define JOINT3_DEFAULT 87


const long MOTOR1_RATIO = (230.0 / 20.0) * 800.0;
const long MOTOR2_RATIO = (150.0 / 20.0) * 15.0 * 800.0;
const long MOTOR3_RATIO = (150.0 / 20.0) * 15.0 * 800.0;
const long MOTOR4_RATIO = (100.0 / 20.0) * 11.0 * 800.0;
const long MOTOR5_RATIO = (100.0 / 20.0) * 11.0 * 800.0;
const long MOTOR6_RATIO = (100.0 / 20.0) * 11.0 * 800.0;
const long MOTOR7_RATIO = 15.0 * 400.0;

AccelStepper steppers[6];
long stepperFullTurn[7] = { MOTOR1_RATIO, MOTOR2_RATIO, MOTOR3_RATIO, MOTOR4_RATIO, MOTOR5_RATIO, MOTOR6_RATIO, MOTOR7_RATIO };
long steppersPos[7] = { 0, 0, 0, 0, 0, 0,0 };
long stepperSpeed[6] = { MOTOR1_MAXSPEED, MOTOR2_MAXSPEED, MOTOR3_MAXSPEED, MOTOR4_MAXSPEED, MOTOR5_MAXSPEED, MOTOR6_MAXSPEED };
long stepperAccel[6] = { MOTOR1_MAXACCEL, MOTOR2_MAXACCEL, MOTOR3_MAXACCEL, MOTOR4_MAXACCEL, MOTOR5_MAXACCEL, MOTOR6_MAXACCEL };
long tempDistance[6] = { 0, 0, 0, 0, 0, 0 };

AccelStepper gripper;


AccelStepper newStepper(int stepPin, int dirPin, int maxSpeed, bool inverted) {
  AccelStepper stepper = AccelStepper(stepper.DRIVER, stepPin, dirPin);
  stepper.setPinsInverted(inverted, inverted, false);
  stepper.setMaxSpeed(maxSpeed);
  stepper.enableOutputs();

  return stepper;
}

void moveDegrees(int stepper, double degree) {
  double steps = stepperFullTurn[stepper] * degree / 360;

  steppersPos[stepper] = long(steps);
}

void setup() {
  Serial.setRxBufferSize(512);
  Serial.begin(115200);
  // put your setup code here, to run once:
  steppers[0] = newStepper(MOTOR1_STEP, MOTOR1_DIR, MOTOR1_MAXSPEED, true);
  steppers[1] = newStepper(MOTOR2_STEP, MOTOR2_DIR, MOTOR2_MAXSPEED, false);
  steppers[2] = newStepper(MOTOR3_STEP, MOTOR3_DIR, MOTOR3_MAXSPEED, true);
  steppers[3] = newStepper(MOTOR4_STEP, MOTOR4_DIR, MOTOR4_MAXSPEED, true);
  steppers[4] = newStepper(MOTOR5_STEP, MOTOR5_DIR, MOTOR5_MAXSPEED, false);
  steppers[5] = newStepper(MOTOR6_STEP, MOTOR6_DIR, MOTOR6_MAXSPEED, false);

  gripper = newStepper(MOTOR7_STEP, MOTOR7_DIR, MOTOR7_MAXSPEED, false);

  initPos();
}


void initPos(){
  moveDegrees(1, -(JOINT2_DEFAULT));
  moveDegrees(2, -(JOINT3_DEFAULT));
  // // move();
  steppers[1].setCurrentPosition(steppersPos[1]);
  steppers[2].setCurrentPosition(steppersPos[2]);

}


float distanceRatio = 0.0;
float longestTime = 0.0;
float longestTimeAtSpeed = 0;

void move(){
  for (int i = 0; i < 6; i++) {
      float distance = abs(steppersPos[i] - steppers[i].currentPosition());


      if (distance != 0) {
        float accelTime = float(stepperSpeed[i]) / float(stepperAccel[i]);
        float accelDist = 0.5 * float(stepperAccel[i]) * pow(accelTime, 2);
        float speedDist = distance - (2 * accelDist);

        float travelTime = speedDist / float(stepperSpeed[i]);

        float totalTime = (accelTime * 2) + travelTime;

        tempDistance[i] = distance;

        if (distance != 0 && totalTime > longestTime) {
          longestTime = totalTime;
          distanceRatio = speedDist / distance;
          longestTimeAtSpeed = travelTime;
        }

        // Serial.print("currentPosition( ");
        // Serial.println(steppers[i].currentPosition());
        // Serial.print("distance ");
        // Serial.println(distance);

        // Serial.print("accelTime ");
        // Serial.println(accelTime);

        // Serial.print("accelDist ");
        // Serial.println(accelDist);

        // Serial.print("speedDist ");
        // Serial.println(speedDist);

        // Serial.print("travelTime ");
        // Serial.println(travelTime);

        // Serial.print("totalTime ");
        // Serial.println(totalTime);

        // Serial.print("longestTime ");
        // Serial.println(longestTime);
        // Serial.print("distanceRatio ");
        // Serial.println(distanceRatio);

        // Serial.print("longestTimeAtSpeed ");
        // Serial.println(longestTimeAtSpeed);
        // Serial.println("");
      } else {
        tempDistance[i] = 0;
      }
      ///D = v*t + 1/2*a*t^2
    }


    for (int i = 0; i < 6; i++) {

      if (tempDistance[i] != 0) {
        long distanceAtSpeed = tempDistance[i] * distanceRatio;
        float travelSpeed = distanceAtSpeed / longestTimeAtSpeed;

        float timeForAccel = (longestTime - longestTimeAtSpeed) / 2;
        float accel = travelSpeed / timeForAccel;

        steppers[i].setSpeed(travelSpeed);
        steppers[i].setAcceleration(accel);
        steppers[i].moveTo(steppersPos[i]);
        // Serial.print("Stepper ");
        // Serial.print(i);
        // Serial.print(" Speed ");
        // Serial.print(travelSpeed);
        // Serial.print(" Accel ");
        // Serial.print(accel);
        // Serial.print("Move TO ");
        // Serial.print(steppersPos[i]);
        // Serial.print("Current pos ");
        // Serial.print(steppers[i].currentPosition());
        // Serial.print("Dist to go ");
        // Serial.print(steppers[i].distanceToGo());
        // Serial.println("");
      } else {
        steppers[i].setSpeed(0);
        steppers[i].setAcceleration(0);
        steppers[i].moveTo(steppersPos[i]);        
      }



      // if (travelSpeed == 0){
      //   travelSpeed = stepperSpeed[i];
      // }
      // if (accel == 0){
      //   accel = stepperAccel[i];
      // }
    }

    while (steppers[0].distanceToGo() != 0 || steppers[1].distanceToGo() != 0 || steppers[2].distanceToGo() != 0 || steppers[3].distanceToGo() != 0 || steppers[4].distanceToGo() != 0 || steppers[5].distanceToGo() != 0) {
      for (int i = 0; i < 6; i++) {
        steppers[i].run();
      }
    }

    gripper.setSpeed(MOTOR7_MAXSPEED);
    gripper.setAcceleration(MOTOR7_MAXACCEL);

    // if (steppersPos[6] > 1700){
    //   steppersPos[6] = 1700;
    // }

    // if (steppersPos[6] < 0){
    //   steppersPos[6] = 0;
    // }

    gripper.moveTo(steppersPos[6]);
    while (gripper.distanceToGo() != 0){
      gripper.run();
    }
}


void loop() {
  // put your main code here, to run repeatedly:
  if (readCommand() == 1) {
    

    
    move();

    
    
    Serial.println("DONE");
  }
}
int readCommand() {
  if (Serial.available()) {
  
    String command = Serial.readStringUntil('\n');
    if (command == "INIT"){
      Serial.println(-(JOINT2_DEFAULT));
      moveDegrees(0,0);
      moveDegrees(1,-(JOINT2_DEFAULT));
      moveDegrees(2,-(JOINT3_DEFAULT));
      moveDegrees(3,0);
      moveDegrees(4,0);
      moveDegrees(5,0);
      moveDegrees(6,0);
      return 1;
    } else if (command == "HOME") {
      moveDegrees(0,0);
      moveDegrees(1,0);
      moveDegrees(2,0);
      moveDegrees(3,0);
      moveDegrees(4,0);
      moveDegrees(5,0);
      moveDegrees(6,0);
      return 1;
    } else if (command.indexOf("GR") >=0){
      int index = command.indexOf("GR");
      double degree = command.substring(index+2).toDouble();
      steppersPos[6] = degree;
      return 1;
    } else if (command.indexOf("RS") >=0){
      int index = command.indexOf("RS");
      double degree = command.substring(index+2).toDouble();
      steppersPos[6] = degree;
      gripper.setCurrentPosition(degree);
      return 1;
    } else {
      int index = command.indexOf(',');
      double degree = command.substring(0, index).toDouble();
      command = command.substring(index + 1);
      moveDegrees(0,degree);

      index = command.indexOf(',');
      degree = command.substring(0, index).toDouble();
      command = command.substring(index + 1);
      moveDegrees(1, degree);


      index = command.indexOf(',');
      degree = command.substring(0, index).toDouble();
      command = command.substring(index + 1);
      moveDegrees(2,degree);


      index = command.indexOf(',');
      degree = command.substring(0, index).toDouble();
      command = command.substring(index + 1);
      // Serial.println(degree);
      moveDegrees(3, degree);


      index = command.indexOf(',');
      degree = command.substring(0, index).toDouble();
      command = command.substring(index + 1);
      // Serial.println(degree);
      moveDegrees(4, degree);

      index = command.indexOf(',');
      degree = command.substring(0, index).toDouble();
      command = command.substring(index + 1);
      // Serial.println(degree);
      moveDegrees(5, degree);
                

      // degree = command.toDouble();
      // Serial.println(degree);
      // // moveDegrees(6, degree);
      // steppersPos[6] = degree;
      return 1;
    }

    
  }

  return 0;
}
