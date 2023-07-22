
#include <ros.h>
#include <robot_arm_hardware/RobotArmCmd.h>
#include <robot_arm_hardware/RobotArmState.h>

#include <AccelStepper.h>
#include <MultiStepper.h>
#include <RotaryEncoder.h>
#include "Queue.h"

//ROS
ros::NodeHandle nh;
robot_arm_hardware::RobotArmCmd robotArmCmd;
robot_arm_hardware::RobotArmState robotArmState;

ros::Publisher robot_arm_state_pub("/robot_arm/state", &robotArmState);


#define ROS_SERIAL true

#define MOTOR_STEPS 800
//Motors PINS
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



#define MOTOR1_MAXSPEED 511
#define MOTOR2_MAXSPEED 3000
#define MOTOR3_MAXSPEED 5000
#define MOTOR4_MAXSPEED 2444
#define MOTOR5_MAXSPEED 2444
#define MOTOR6_MAXSPEED 2444
#define MOTOR7_MAXSPEED 3000

#define JOINT2_DEFAULT 55
#define JOINT3_DEFAULT -87



// #define ENCODER1_PINA 5
// #define ENCODER1_PINB 18


// #define ENCODER2_PINA 22
// #define ENCODER2_PINB 23


const long MOTOR1_RATIO = (230.0 / 20.0) * 1600.0;
const long MOTOR2_RATIO = (150.0 / 20.0) * 15.0 * 1600.0;
const long MOTOR3_RATIO = (150.0 / 20.0) * 15.0 * 1600.0;
const long MOTOR4_RATIO = (100.0 / 20.0) * 11.0 * 1600.0;
const long MOTOR5_RATIO = (100.0 / 20.0) * 11.0 * 1600.0;
const long MOTOR6_RATIO = (100.0 / 20.0) * 11.0 * 1600.0;

const long ENCODER1_RATIO = (230.0 / 20.0) * 1200.0;
const long ENCODER2_RATIO = (150.0 / 20.0) * 1200.0;



const int JstepPin[6] = { MOTOR1_STEP, MOTOR2_STEP, MOTOR3_STEP, MOTOR4_STEP, MOTOR5_STEP, MOTOR6_STEP };
const int JdirPin[6] = { MOTOR1_DIR, MOTOR2_DIR, MOTOR3_DIR, MOTOR4_DIR, MOTOR5_DIR, MOTOR6_DIR };
int JCurrPos[6] = { 0, 0, 0, 0, 0, 0 };
int steps[6] = { 0, 0, 0, 0, 0, 0 };
int preSteps[6] = { 0, 0, 0, 0, 0, 0 };

float SpeedIn = 200;
float ACCdur = 0;
float ACCspd = 50;
float DCCdur = 0;
float DCCspd = 50;
const int SpeedMult = 200;

Queue<robot_arm_hardware::RobotArmCmd> queue(1024);

AccelStepper steppers[6];
MultiStepper msteppers;

// RotaryEncoder *encoder1 = nullptr;
// RotaryEncoder *encoder2 = nullptr;

long stepperFullTurn[6] = { MOTOR1_RATIO, MOTOR2_RATIO, MOTOR3_RATIO, MOTOR4_RATIO, MOTOR5_RATIO, MOTOR6_RATIO };
long encoderFullTurn[2] = { ENCODER1_RATIO, ENCODER2_RATIO };
long steppersPos[6] = { 0, 0, 0, 0, 0, 0 };

AccelStepper gripper;


AccelStepper newStepper(int stepPin, int dirPin, int maxSpeed, bool inverted) {
  AccelStepper stepper = AccelStepper(stepper.DRIVER, stepPin, dirPin);
  stepper.setPinsInverted(inverted, inverted, false);
  stepper.setMaxSpeed(maxSpeed);
  stepper.setSpeed(maxSpeed);
  stepper.setAcceleration(maxSpeed);
  stepper.enableOutputs();

  return stepper;
}

// IRAM_ATTR void encoder1Position()
// {
//   encoder1->tick(); // just call tick() to check the state.
// }

// IRAM_ATTR void encoder2Position()
// {
//   encoder2->tick(); // just call tick() to check the state.
// }


void publish_robot_state() {
  // encoder1->tick();
  // encoder2->tick();
  // long encoder1CurrentPos = encoder1->getPosition() ;
  // long encoder2CurrentPos = encoder2->getPosition() ;

  // double encoder1Angle = encoder1CurrentPos *  360.0 /ENCODER1_RATIO;
  // double encoder2Angle = encoder2CurrentPos *  360.0 /ENCODER2_RATIO;
  // robotArmState.pos[0] = -(stepsToDegree(0, JCurrPos[0]));
  // robotArmState.pos[1] = (stepsToDegree(1, JCurrPos[1]));
  // robotArmState.pos[2] = -(stepsToDegree(2, JCurrPos[2]));
  // robotArmState.pos[3] = -(stepsToDegree(3, JCurrPos[3]));
  // robotArmState.pos[4] = -(stepsToDegree(4, JCurrPos[4]));
  // robotArmState.pos[5] = -(stepsToDegree(5, JCurrPos[5]));
  robotArmState.pos[0] = -(stepsToDegree(0, steppers[0].currentPosition()));
  robotArmState.pos[1] = (stepsToDegree(1, steppers[1].currentPosition()));
  robotArmState.pos[2] = -(stepsToDegree(2, steppers[2].currentPosition()));
  robotArmState.pos[3] = -(stepsToDegree(3, steppers[3].currentPosition()));
  robotArmState.pos[4] = -(stepsToDegree(4, steppers[4].currentPosition()));
  robotArmState.pos[5] = -(stepsToDegree(5, steppers[5].currentPosition()));
  // robotArmState.pos[6] = -(stepsToDegree(5, steppers[5].currentPosition()));

  robot_arm_state_pub.publish(&robotArmState);
  // msteppers.run();
}




void moveMotor(int Jstep[], int incDec[]) {
  int Jcur[6] = { 0, 0, 0, 0, 0, 0 };


  int Jactives[6] = { 0, 0, 0, 0, 0, 0 };
  int Jactive = 0;

  for (int i = 0; i < 6; i++) {
    if (Jstep[i] != Jcur[i]) {
      Jactives[i] = 1;
    }
    Jactive += Jactives[i];
  }


  int J_PE[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_1[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_2[6] = { 0, 0, 0, 0, 0, 0 };

  int J_LO_1[6] = { 0, 0, 0, 0, 0, 0 };

  int J_LO_2[6] = { 0, 0, 0, 0, 0, 0 };

  //reset

  int J_PEcur[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_1cur[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_2cur[6] = { 0, 0, 0, 0, 0, 0 };

  int highStepCur = 0;
  float curDelay = 0;

  int HighStep = Jstep[0];
  if (Jstep[1] > HighStep) {
    HighStep = Jstep[1];
  }
  if (Jstep[2] > HighStep) {
    HighStep = Jstep[2];
  }
  if (Jstep[3] > HighStep) {
    HighStep = Jstep[3];
  }
  if (Jstep[4] > HighStep) {
    HighStep = Jstep[4];
  }
  if (Jstep[5] > HighStep) {
    HighStep = Jstep[5];
  }


  /////CALC SPEEDS//////
  float ACCStep = (HighStep * (ACCdur / 100));
  float DCCStep = HighStep - (HighStep * (DCCdur / 100));
  float AdjSpeed = (SpeedIn / 100);
  //REG SPEED
  float CalcRegSpeed = (SpeedMult / AdjSpeed);
  int REGSpeed = int(CalcRegSpeed);

  //ACC SPEED
  float ACCspdT = (ACCspd / 100);
  float CalcACCSpeed = ((SpeedMult + (SpeedMult / ACCspdT)) / AdjSpeed);
  float ACCSpeed = (CalcACCSpeed);
  float ACCinc = (REGSpeed - ACCSpeed) / ACCStep;

  //DCC SPEED
  float DCCspdT = (DCCspd / 100);
  float CalcDCCSpeed = ((SpeedMult + (SpeedMult / DCCspdT)) / AdjSpeed);
  float DCCSpeed = (CalcDCCSpeed);
  float DCCinc = (REGSpeed + DCCSpeed) / DCCStep;
  DCCSpeed = REGSpeed;

  while (Jcur[0] < Jstep[0] || Jcur[1] < Jstep[1] || Jcur[2] < Jstep[2] || Jcur[3] < Jstep[3] || Jcur[4] < Jstep[4] || Jcur[5] < Jstep[5]) {

    ////DELAY CALC/////
    if (highStepCur <= ACCStep) {
      curDelay = (ACCSpeed / Jactive);
      ACCSpeed = ACCSpeed + ACCinc;
    } else if (highStepCur >= DCCStep) {
      curDelay = (DCCSpeed / Jactive);
      DCCSpeed = DCCSpeed + DCCinc;
    } else {
      curDelay = (REGSpeed / Jactive);
    }
    // curDelay = 4000;

    for (int i = 0; i < 6; i++) {
      ///find pulse every
      if (Jcur[i] < Jstep[i]) {
        J_PE[i] = (HighStep / Jstep[i]);
        ///find left over 1
        J_LO_1[i] = (HighStep - (Jstep[i] * J_PE[i]));
        ///find skip 1
        if (J_LO_1[i] > 0) {
          J_SE_1[i] = (HighStep / J_LO_1[i]);
        } else {
          J_SE_1[i] = 0;
        }
        ///find left over 2
        if (J_SE_1[i] > 0) {
          J_LO_2[i] = HighStep - ((Jstep[i] * J_PE[i]) + ((Jstep[i] * J_PE[i]) / J_SE_1[i]));
        } else {
          J_LO_2[i] = 0;
        }
        ///find skip 2
        if (J_LO_2[i] > 0) {
          J_SE_2[i] = (HighStep / J_LO_2[i]);
        } else {
          J_SE_2[i] = 0;
        }
        /////////  J1  ///////////////
        if (J_SE_2[i] == 0) {
          J_SE_2cur[i] = (J_SE_2[i] + 1);
        }
        if (J_SE_2cur[i] != J_SE_2[i]) {
          J_SE_2cur[i] = ++J_SE_2cur[i];
          if (J_SE_1[i] == 0) {
            J_SE_1cur[i] = (J_SE_1[i] + 1);
          }
          if (J_SE_1cur[i] != J_SE_1[i]) {
            J_SE_1cur[i] = ++J_SE_1cur[i];
            J_PEcur[i] = ++J_PEcur[i];
            if (J_PEcur[i] == J_PE[i]) {
              Jcur[i] = ++Jcur[i];
              if (JCurrPos[i] >= 0 && incDec[i] == 0) {
                JCurrPos[i] = JCurrPos[i] - 1;
              } else if (JCurrPos[i] < 0 && incDec[i] == 0) {
                JCurrPos[i] = JCurrPos[i] + (-1);
              } else if (JCurrPos[i] >= 0 && incDec[i] == 1) {
                JCurrPos[i] = JCurrPos[i] + 1;
              } else if (JCurrPos[i] <= 0 && incDec[i] == 1) {
                JCurrPos[i] = JCurrPos[i] - (-1);
              }
              J_PEcur[i] = 0;

              digitalWrite(JstepPin[i], LOW);
              // Serial.println(curDelay);
              delayMicroseconds(curDelay);
              digitalWrite(JstepPin[i], HIGH);
              delayMicroseconds(curDelay);
            }
          } else {
            J_SE_1cur[i] = 0;
          }
        } else {
          J_SE_2cur[i] = 0;
        }
      }
    }

    highStepCur = ++highStepCur;
  }
}

void moveMotor2(int Jstep[], int incDec[]) {
  int Jcur[6] = { 0, 0, 0, 0, 0, 0 };


  int Jactives[6] = { 0, 0, 0, 0, 0, 0 };
  int Jactive = 0;

  for (int i = 0; i < 6; i++) {
    if (Jstep[i] != Jcur[i]) {
      Jactives[i] = 1;
    }
    Jactive += Jactives[i];
  }


  int J_PE[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_1[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_2[6] = { 0, 0, 0, 0, 0, 0 };

  int J_LO_1[6] = { 0, 0, 0, 0, 0, 0 };

  int J_LO_2[6] = { 0, 0, 0, 0, 0, 0 };

  //reset

  int J_PEcur[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_1cur[6] = { 0, 0, 0, 0, 0, 0 };
  int J_SE_2cur[6] = { 0, 0, 0, 0, 0, 0 };

  int highStepCur = 0;
  float curDelay = 0;

  int HighStep = Jstep[0];
  if (Jstep[1] > HighStep) {
    HighStep = Jstep[1];
  }
  if (Jstep[2] > HighStep) {
    HighStep = Jstep[2];
  }
  if (Jstep[3] > HighStep) {
    HighStep = Jstep[3];
  }
  if (Jstep[4] > HighStep) {
    HighStep = Jstep[4];
  }
  if (Jstep[5] > HighStep) {
    HighStep = Jstep[5];
  }


  // /////CALC SPEEDS//////
  // float ACCStep = (HighStep * (ACCdur / 100));
  // float DCCStep = HighStep - (HighStep * (DCCdur / 100));
  // float AdjSpeed = (SpeedIn / 100);
  // //REG SPEED
  // float CalcRegSpeed = (SpeedMult / AdjSpeed);
  // int REGSpeed = int(CalcRegSpeed);

  // //ACC SPEED
  // float ACCspdT = (ACCspd / 100);
  // float CalcACCSpeed = ((SpeedMult + (SpeedMult / ACCspdT)) / AdjSpeed);
  // float ACCSpeed = (CalcACCSpeed);
  // float ACCinc = (REGSpeed - ACCSpeed) / ACCStep;

  // //DCC SPEED
  // float DCCspdT = (DCCspd / 100);
  // float CalcDCCSpeed = ((SpeedMult + (SpeedMult / DCCspdT)) / AdjSpeed);
  // float DCCSpeed = (CalcDCCSpeed);
  // float DCCinc = (REGSpeed + DCCSpeed) / DCCStep;
  // DCCSpeed = REGSpeed;
  float AdjSpeed = (SpeedIn / 100);
  //REG SPEED
  float LspeedAdj = 3;
  float CalcRegSpeed = ((SpeedMult * LspeedAdj) / AdjSpeed);
  curDelay = int(CalcRegSpeed) / Jactive;
  while (Jcur[0] < Jstep[0] || Jcur[1] < Jstep[1] || Jcur[2] < Jstep[2] || Jcur[3] < Jstep[3] || Jcur[4] < Jstep[4] || Jcur[5] < Jstep[5]) {

    ////DELAY CALC/////
    // if (highStepCur <= ACCStep) {
    //   curDelay = (ACCSpeed / Jactive);
    //   ACCSpeed = ACCSpeed + ACCinc;
    // } else if (highStepCur >= DCCStep) {
    //   curDelay = (DCCSpeed / Jactive);
    //   DCCSpeed = DCCSpeed + DCCinc;
    // } else {
    //   curDelay = (REGSpeed / Jactive);
    // }
    // curDelay = 4000;

    for (int i = 0; i < 6; i++) {
      ///find pulse every
      if (Jcur[i] < Jstep[i]) {
        J_PE[i] = (HighStep / Jstep[i]);
        ///find left over 1
        J_LO_1[i] = (HighStep - (Jstep[i] * J_PE[i]));
        ///find skip 1
        if (J_LO_1[i] > 0) {
          J_SE_1[i] = (HighStep / J_LO_1[i]);
        } else {
          J_SE_1[i] = 0;
        }
        ///find left over 2
        if (J_SE_1[i] > 0) {
          J_LO_2[i] = HighStep - ((Jstep[i] * J_PE[i]) + ((Jstep[i] * J_PE[i]) / J_SE_1[i]));
        } else {
          J_LO_2[i] = 0;
        }
        ///find skip 2
        if (J_LO_2[i] > 0) {
          J_SE_2[i] = (HighStep / J_LO_2[i]);
        } else {
          J_SE_2[i] = 0;
        }
        /////////  J1  ///////////////
        if (J_SE_2[i] == 0) {
          J_SE_2cur[i] = (J_SE_2[i] + 1);
        }
        if (J_SE_2cur[i] != J_SE_2[i]) {
          J_SE_2cur[i] = ++J_SE_2cur[i];
          if (J_SE_1[i] == 0) {
            J_SE_1cur[i] = (J_SE_1[i] + 1);
          }
          if (J_SE_1cur[i] != J_SE_1[i]) {
            J_SE_1cur[i] = ++J_SE_1cur[i];
            J_PEcur[i] = ++J_PEcur[i];
            if (J_PEcur[i] == J_PE[i]) {
              Jcur[i] = ++Jcur[i];
              if (JCurrPos[i] >= 0 && incDec[i] == 0) {
                JCurrPos[i] = JCurrPos[i] - 1;
              } else if (JCurrPos[i] < 0 && incDec[i] == 0) {
                JCurrPos[i] = JCurrPos[i] + (-1);
              } else if (JCurrPos[i] >= 0 && incDec[i] == 1) {
                JCurrPos[i] = JCurrPos[i] + 1;
              } else if (JCurrPos[i] <= 0 && incDec[i] == 1) {
                JCurrPos[i] = JCurrPos[i] - (-1);
              }
              J_PEcur[i] = 0;

              digitalWrite(JstepPin[i], LOW);
              // Serial.println(curDelay);
              delayMicroseconds(curDelay);
              digitalWrite(JstepPin[i], HIGH);
              delayMicroseconds(curDelay);
            }
          } else {
            J_SE_1cur[i] = 0;
          }
        } else {
          J_SE_2cur[i] = 0;
        }
      }
    }

    highStepCur = ++highStepCur;
  }
}




float prePos[6] = { 0, 0, 0, 0, 0 };

void robot_arm_cmd_callback(const robot_arm_hardware::RobotArmCmd& cmd) {
  boolean diff = false;
  for (int i; i < 6; i++) {
    if (diff == true || prePos[i] != cmd.pos[i]) {
      diff = true;
      prePos[i] = cmd.pos[i];
    }
  }

  if (diff) {
    queue.push(cmd);
    nh.loginfo("PUSH");
  }
}

ros::Subscriber<robot_arm_hardware::RobotArmCmd> robot_arm_cmd_sub("/robot_arm/cmd", &robot_arm_cmd_callback);


void setup() {

  if (!ROS_SERIAL) {
    Serial.begin(9600);
  } else {
    nh.getHardware()->setBaud(115200);
    nh.initNode();
    nh.advertise(robot_arm_state_pub);
    nh.subscribe(robot_arm_cmd_sub);
    nh.loginfo("RESTART!!");
  }


  // put your setup code here, to run once:
  steppers[0] = newStepper(MOTOR1_STEP, MOTOR1_DIR, MOTOR1_MAXSPEED, true);
  steppers[1] = newStepper(MOTOR2_STEP, MOTOR2_DIR, MOTOR2_MAXSPEED, true);
  steppers[2] = newStepper(MOTOR3_STEP, MOTOR3_DIR, MOTOR3_MAXSPEED, true);
  steppers[3] = newStepper(MOTOR4_STEP, MOTOR4_DIR, MOTOR4_MAXSPEED, true);
  steppers[4] = newStepper(MOTOR5_STEP, MOTOR5_DIR, MOTOR5_MAXSPEED, true);
  steppers[5] = newStepper(MOTOR6_STEP, MOTOR6_DIR, MOTOR6_MAXSPEED, true);

  // gripper = newStepper(MOTOR7_STEP, MOTOR7_DIR, MOTOR7_MAXSPEED, true);

  msteppers.addStepper(steppers[0]);
  msteppers.addStepper(steppers[1]);
  msteppers.addStepper(steppers[2]);
  msteppers.addStepper(steppers[3]);
  msteppers.addStepper(steppers[4]);
  msteppers.addStepper(steppers[5]);
  // encoder1 = new RotaryEncoder(ENCODER1_PINA, ENCODER1_PINB, RotaryEncoder::LatchMode::TWO03);
  // encoder2 = new RotaryEncoder(ENCODER2_PINA, ENCODER2_PINB, RotaryEncoder::LatchMode::TWO03);

  // attachInterrupt(digitalPinToInterrupt(ENCODER1_PINA), encoder1Position, CHANGE);
  // attachInterrupt(digitalPinToInterrupt(ENCODER1_PINB), encoder1Position, CHANGE);

  // attachInterrupt(digitalPinToInterrupt(ENCODER2_PINA), encoder2Position, CHANGE);
  // attachInterrupt(digitalPinToInterrupt(ENCODER2_PINB), encoder2Position, CHANGE);


  // encoder1->setPosition(0);
  // encoder2->setPosition(0);

  //  Serial.print(encoder1->getPosition());

  for (int i = 0; i < 6; i++) {
    pinMode(JstepPin[i], OUTPUT);
    pinMode(JdirPin[i], OUTPUT);
  }

  initPos();

  if (ROS_SERIAL) {
    nh.loginfo("Connected to HARDWARE!!");
  }
}

void runSteppers() {
  msteppers.run();
}


void moveDegrees(int stepper, double degree) {
  double steps = stepperFullTurn[stepper] * degree / 360;

  steppersPos[stepper] = long(steps);
}


double stepsToDegree(int stepper, long steps) {
  double degree = ((double)steps / (double)stepperFullTurn[stepper]) * 360.0;

  return degree;
}


long tempStepperPos = 0;
double tempEncoderPos = 0;

int isInit = 0;
int initDone = 0;


void calculatePos() {
  // int absSteps[6] = { 0, 0, 0, 0, 0, 0 };
  // int inDec[6] = { 1, 1, 1, 1, 1, 1 };  //default increase
  // for (int i = 0; i < 6; i++) {

  //   if (JCurrPos[i] >= 0 && steppersPos[i] >= 0) {  //both positive
  //     if (JCurrPos[i] > steppersPos[i]) {           //curr pos higher then target pos, then reverse
  //       digitalWrite(JdirPin[i], HIGH);             //anti clockwise
  //       inDec[i] = 0;
  //       absSteps[i] = JCurrPos[i] - steppersPos[i];

  //     } else {                          //curr pos lower then target pos, then forward
  //       digitalWrite(JdirPin[i], LOW);  //clockwise
  //       absSteps[i] = steppersPos[i] - JCurrPos[i];
  //       inDec[i] = 1;
  //     }
  //   } else if (JCurrPos[i] < 0 && steppersPos[i] < 0) {  //both negative
  //     if (JCurrPos[i] > steppersPos[i]) {                //curr pos higher then target pos, then forward
  //       digitalWrite(JdirPin[i], HIGH);                  //anti clockwise
  //       absSteps[i] = JCurrPos[i] - steppersPos[i];
  //       inDec[i] = 0;
  //     } else {
  //       digitalWrite(JdirPin[i], LOW);  //clockwise
  //       absSteps[i] = steppersPos[i] - JCurrPos[i];
  //       inDec[i] = 1;
  //     }
  //   } else if (JCurrPos[i] >= 0 && steppersPos[i] <= 0) {  //Curr positive, target negative, then anti clockwise
  //     digitalWrite(JdirPin[i], HIGH);                      //anti clockwise
  //     absSteps[i] = JCurrPos[i] - steppersPos[i];
  //     inDec[i] = 0;
  //   } else if (JCurrPos[i] <= 0 && steppersPos[i] >= 0) {  //Curr Negative, target Positive, then clockwise
  //     digitalWrite(JdirPin[i], LOW);                       //clockwise
  //     absSteps[i] = steppersPos[i] - JCurrPos[i];
  //     inDec[i] = 1;
  //   }
  // }
  // moveMotor2(absSteps, inDec);
  msteppers.moveTo(steppersPos);
  msteppers.runSpeedToPosition();
}


void initPos() {
  // isInit = 1;
  // initDone = 0;
  moveDegrees(1, JOINT2_DEFAULT);
  moveDegrees(2, JOINT3_DEFAULT);
  // calculatePos();

  JCurrPos[1] = 0;
  JCurrPos[2] = 0;
  msteppers.moveTo(steppersPos);
  msteppers.runSpeedToPosition();

  // steppers[1].moveTo(steppersPos[1]);  
  // steppers[2].moveTo(steppersPos[2]);  
    // while (
    //   steppers[0].distanceToGo() != 0 || steppers[1].distanceToGo() != 0 || steppers[2].distanceToGo() != 0 || steppers[3].distanceToGo() != 0 || steppers[4].distanceToGo() != 0 || steppers[5].distanceToGo() != 0) {
    //   for (int i = 0; i < 6; i++) {
    //     steppers[i].run();
    //   }
    // }



  steppers[1].setCurrentPosition(JOINT2_DEFAULT);
  steppers[2].setCurrentPosition(JOINT3_DEFAULT);
  // moveDegrees(1, 0);
  // moveDegrees(2, 0);
  // isInit = 0;
}






unsigned long delaytime = millis();
void loop() {

  if (ROS_SERIAL) {
    nh.spinOnce();
  } else {
    readCommand();
  }
  // encoder1->tick();
  if (isInit == 0) {


    // double encoder1Pos = long(encoder1Angle *  stepperFullTurn[0] /360.0);


    // Serial.print(",");
    // Serial.println(0.9*stepper1CurrentPos + 0.1*encoder1Pos);
    // long newPos = (0.85*stepper1CurrentPos + 0.15*encoder1Pos);
    // if (!steppers[0].run()){
    // steppers[0].setCurrentPosition(newPos);
    //   steppers[0].moveTo(steppersPos[0]);
    // }


    // long stepper2CurrentPos = steppers[1].currentPosition();
    // long encoder2CurrentPos = encoder2->getPosition() ;

    // double encoder2Angle = encoder2CurrentPos *  360.0 /ENCODER2_RATIO;
    // double encoder2Pos = encoder2Angle *  stepperFullTurn[1] /360.0;

    // Serial.print("Motor Pos: ");
    // Serial.println(stepper2CurrentPos);
    // Serial.print("Encoder Pos: ");
    // Serial.println(encoder2Angle);
    // if (!steppers[1].run()){
    // steppers[1].setCurrentPosition((0.1*encoder2Pos));
    //   steppers[1].moveTo(steppersPos[1]);
    // }

    // nh.loginfo("NOT RUNNING");
    if (queue.count() > 0) {
      robot_arm_hardware::RobotArmCmd cmd = queue.pop();
      // Serial.println(cmd.pos[0]);
      moveDegrees(0, -(cmd.pos[0]));
      moveDegrees(1, (cmd.pos[1]));
      moveDegrees(2, -(cmd.pos[2]));
      moveDegrees(3, -(cmd.pos[3]));
      moveDegrees(4, -(cmd.pos[4]));
      moveDegrees(5, -(cmd.pos[5]));

      for (int i = 0; i < 6; i++) {
        steppers[i].moveTo(steppersPos[i]);
      }

      // while (steppers[0].distanceToGo() != 0 || steppers[1].distanceToGo() != 0 || steppers[2].distanceToGo() != 0 || steppers[3].distanceToGo() != 0 || steppers[4].distanceToGo() != 0 || steppers[5].distanceToGo() != 0) {
      //   for (int i = 0; i < 6; i++) {
      //     steppers[i].run();
      //   }
      // }

      // int absSteps[6] = { 0, 0, 0, 0, 0, 0 };
      // int inDec[6] = { 1, 1, 1, 1, 1, 1 };  //default increase
      // for (int i = 0; i < 6; i++) {

      //   if (JCurrPos[i] >= 0 && steppersPos[i] >= 0) {  //both positive
      //     if (JCurrPos[i] > steppersPos[i]) {           //curr pos higher then target pos, then reverse
      //       digitalWrite(JdirPin[i], HIGH);             //anti clockwise
      //       inDec[i] = 0;
      //       absSteps[i] = JCurrPos[i] - steppersPos[i];

      //     } else {                          //curr pos lower then target pos, then forward
      //       digitalWrite(JdirPin[i], LOW);  //clockwise
      //       absSteps[i] = steppersPos[i] - JCurrPos[i];
      //       inDec[i] = 1;
      //     }
      //   } else if (JCurrPos[i] < 0 && steppersPos[i] < 0) {  //both negative
      //     if (JCurrPos[i] > steppersPos[i]) {                //curr pos higher then target pos, then forward
      //       digitalWrite(JdirPin[i], HIGH);                  //anti clockwise
      //       absSteps[i] = JCurrPos[i] - steppersPos[i];
      //       inDec[i] = 0;
      //     } else {
      //       digitalWrite(JdirPin[i], LOW);  //clockwise
      //       absSteps[i] = steppersPos[i] - JCurrPos[i];
      //       inDec[i] = 1;
      //     }
      //   } else if (JCurrPos[i] >= 0 && steppersPos[i] <= 0) {  //Curr positive, target negative, then anti clockwise
      //     digitalWrite(JdirPin[i], HIGH);                      //anti clockwise
      //     absSteps[i] = JCurrPos[i] - steppersPos[i];
      //     inDec[i] = 0;
      //   } else if (JCurrPos[i] <= 0 && steppersPos[i] >= 0) {  //Curr Negative, target Positive, then clockwise
      //     digitalWrite(JdirPin[i], LOW);                       //clockwise
      //     absSteps[i] = steppersPos[i] - JCurrPos[i];
      //     inDec[i] = 1;
      //   }
      // }
      // moveMotor(absSteps, inDec);
      calculatePos();

      //       Serial.print("Curr Pos: ");
      //       Serial.print(JCurrPos[0]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[1]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[2]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[3]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[4]);
      //       Serial.print(",");
      //       Serial.println(JCurrPos[5]);

      //       Serial.print("Steps: ");
      //       Serial.print(absSteps[0]);
      //       Serial.print(",");
      //       Serial.print(absSteps[1]);
      //       Serial.print(",");
      //       Serial.print(absSteps[2]);
      //       Serial.print(",");
      //       Serial.print(absSteps[3]);
      //       Serial.print(",");
      //       Serial.print(absSteps[4]);
      //       Serial.print(",");
      //       Serial.println(absSteps[5]);


      //  Serial.print("Curr Pos: ");
      //       Serial.print(JCurrPos[0]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[1]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[2]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[3]);
      //       Serial.print(",");
      //       Serial.print(JCurrPos[4]);
      //       Serial.print(",");
      //       Serial.println(JCurrPos[5]);

      //       Serial.print("Steps: ");
      //       Serial.print(absSteps[0]);
      //       Serial.print(",");
      //       Serial.print(absSteps[1]);
      //       Serial.print(",");
      //       Serial.print(absSteps[2]);
      //       Serial.print(",");
      //       Serial.print(absSteps[3]);
      //       Serial.print(",");
      //       Serial.print(absSteps[4]);
      //       Serial.print(",");
      //       Serial.println(absSteps[5]);
      // msteppers.moveTo(steppersPos);
      // msteppers.runSpeedToPosition();
      // Serial.print(cmd.pos[6]);
      // gripper.setSpeed(500);
      // gripper.moveTo(cmd.pos[6]);
      // gripper.runToPosition();
    }

    // while (
    //   steppers[0].distanceToGo() != 0 || steppers[1].distanceToGo() != 0 || steppers[2].distanceToGo() != 0 || steppers[3].distanceToGo() != 0 || steppers[4].distanceToGo() != 0 || steppers[5].distanceToGo() != 0) {
    //   for (int i = 0; i < 6; i++) {
    //     steppers[i].run();
    //   }
    // }

    // for (int i = 0; i < 6; i++) {
    //     steppers[i].run();
    //   }





    //  encoder1->tick();
    //  double stepperCurrDegree =((double) steppers[0].currentPosition() * 360.0/ (double)stepperFullTurn[0]) ;
    //  long encoder1CurrentPos = encoder1->getPosition() ;
    //  double encoderCurrDegree =  (encoder1CurrentPos) * 360.0 /encoderFullTurn[0] ;
    //  double error = encoderCurrDegree - stepperCurrDegree;

    //  double p_term = MOTOR1_KP * error;
    //  integral += p_term;
    //  double i_term = MOTOR1_KI * integral;
    //  double d_term = MOTOR1_KD * (error - pre_error);
    //  pre_error = error;

    //  double correction = p_term + i_term + d_term;
    //  double steps = stepperFullTurn[0] * correction / 360;

    //  if (preSteps != steps){
    //   //  Serial.print("Encoder:");
    //   //  Serial.println(encoder1CurrentPos);
    //   //  Serial.print("Correctoin:");
    //   //  Serial.print(correction);
    //   //  Serial.println(steps);

    //     preSteps = steps;
    //  }

    //  steppersPos[0] = steps;


    // char log_msg[50];
    //  sprintf(log_msg,"motor= %d, encoder= %d ", stepper1CurrentPos, encoderSteps);

    // if (abs(diff) > 10) {
    //   if (stepper1CurrentPos > 0){
    //     steppers[0].setCurrentPosition(stepper1CurrentPos + diff);
    //   } else {
    //     steppers[0].setCurrentPosition(stepper1CurrentPos - diff);
    //   }
    // }


    // msteppers.runSpeedToPosition();
    //   boolean done = false;
    // while (!done){
    //   done = true;
    //   for(int i = 0; i < 6; i++){

    //     if (steppers[i].distanceToGo() != 0){
    //       steppers[i].runSpeed();
    //       done = false;


    //     } else {
    // 	    steppers[i].setCurrentPosition(steppers[i].currentPosition());
    //     }
    //   }

    //   publish_robot_state();
    //   nh.spinOnce();
    // }
    //  msteppers.run();
    //  nh.spinOnce();
    //  msteppers.runSpeedToPosition();
    // runSteppers();
    // if (!msteppers.run()){
    // if (tempStepperPos != stepper1CurrentPos){
    //   Serial.print("Motor Pos: ");
    //   Serial.print(stepper1CurrentPos);
    //   Serial.print(", ");
    //   Serial.print("Motor Angle: ");
    //   Serial.print(stepper1Angle);
    //   Serial.print(", ");
    //   Serial.print("Encoder Step Pos: ");
    //   Serial.print(encoder1Pos);
    //   Serial.print("Encoder Angle: ");
    //   Serial.print(encoder1Angle);
    //   Serial.print("New Pos : ");
    //   Serial.print((encoder1->getPosition() * MOTOR1_RATIO)/ENCODER1_RATIO);
    //   Serial.print("Encoder Pos: ");
    //   Serial.println(encoder1->getPosition());
    //   tempStepperPos = stepper1CurrentPos;
    // }
    // }

    // steppers[0].run();
    // steppers[1].run();
    // steppers[2].run();
    // steppers[3].run();

    // for (int i = 0; i < 6; i++){
    //   steppers[i].moveTo(steppersPos[i]);
    // }

    // for (int i = 0; i < 6; i++){
    //   steppers[i].run();
    // }


    if (ROS_SERIAL) {
      publish_robot_state();
      nh.spinOnce();
    }

    // steppers[1].moveTo(steppersPos[1]);
    // steppers[2].moveTo(steppersPos[2]);
    // steppers[3].moveTo(steppersPos[3]);
  }
  // encoder1->tick();
  // encoder2->tick();
}

Queue<String> queue(1024);
void readCommand() {
  while (Serial.available()){
    String command = Serial.readStringUntil('\n');
    queue.push(const RobotArmCmd &item)
  } 

  

  if (queue.count() > 0) {

    robot_arm_hardware::RobotArmCmd cmd = robot_arm_hardware::RobotArmCmd();

    String command = Serial.readStringUntil('\n');

    int index = command.indexOf(',');
    double degree = command.substring(0, index).toDouble();
    command = command.substring(index + 1);
    cmd.pos[0] = degree;

    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();
    command = command.substring(index + 1);
    cmd.pos[1] = degree;


    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();
    command = command.substring(index + 1);
    cmd.pos[2] = degree;


    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();
    command = command.substring(index + 1);
    // Serial.println(degree);
    cmd.pos[3] = degree;


    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();
    command = command.substring(index + 1);
    // Serial.println(degree);
    cmd.pos[4] = degree;


    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();
    command = command.substring(index + 1);
    // Serial.println(degree);
    cmd.pos[5] = degree;


    degree = command.toDouble();
    cmd.pos[6] = degree;
    Serial.println(degree);
    // steppers[0].setCurrentPosition(stepper1CurrentPos);
    // steppers[0].moveTo(steppersPos[0]);
    // steppers[1].moveTo(steppersPos[1]);
    // steppers[2].moveTo(steppersPos[2]);
    // steppers[3].moveTo(steppersPos[3]);
    queue.push(cmd);
  }
}
