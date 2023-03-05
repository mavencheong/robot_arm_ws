
#include <ros.h>
#include <robot_arm_hardware/RobotArmCmd.h>
#include <robot_arm_hardware/RobotArmState.h>

#include <AccelStepper.h>
#include <MultiStepper.h>
#include <RotaryEncoder.h>


//ROS
ros::NodeHandle nh;
robot_arm_hardware::RobotArmCmd robotArmCmd;
robot_arm_hardware::RobotArmState robotArmState;

ros::Publisher robot_arm_state_pub("/robot_arm/state", &robotArmState);


#define ROS_SERIAL true

#define MOTOR_STEPS 800
//Motors PINS
#define MOTOR1_DIR  12
#define MOTOR1_STEP 13

#define MOTOR2_DIR 27
#define MOTOR2_STEP 14

#define MOTOR3_DIR 25
#define MOTOR3_STEP 26


#define MOTOR4_DIR 4
#define MOTOR4_STEP 15

#define MOTOR5_DIR 32
#define MOTOR5_STEP 33

#define MOTOR6_DIR 21
#define MOTOR6_STEP 19



#define MOTOR1_MAXSPEED 5000
#define MOTOR2_MAXSPEED 5000
#define MOTOR3_MAXSPEED 5000
#define MOTOR4_MAXSPEED 5000
#define MOTOR5_MAXSPEED 5000
#define MOTOR6_MAXSPEED 5000


#define ENCODER1_PINA 5
#define ENCODER1_PINB 18


#define ENCODER2_PINA 22
#define ENCODER2_PINB 23



const long MOTOR1_RATIO = (230.0 / 20.0) * 1600.0;
const long MOTOR2_RATIO = (150.0 /20.0) * 15.0 * 1600.0; 
const long MOTOR3_RATIO = (150.0 /20.0) * 15.0 * 1600.0; 
const long MOTOR4_RATIO = (100.0 /20.0) * 11.0 * 1600.0; 
const long MOTOR5_RATIO = (100.0 /20.0) * 11.0 * 1600.0; 
const long MOTOR6_RATIO = (100.0 /20.0) * 11.0 * 1600.0; 

const long ENCODER1_RATIO = (230.0 /20.0) * 1200.0;
const long ENCODER2_RATIO = (150.0 /20.0) * 1200.0;



AccelStepper steppers[6];
MultiStepper msteppers;

RotaryEncoder *encoder1 = nullptr;
// RotaryEncoder *encoder2 = nullptr;

long stepperFullTurn[6] = {MOTOR1_RATIO, MOTOR2_RATIO, MOTOR3_RATIO, MOTOR4_RATIO, MOTOR5_RATIO, MOTOR6_RATIO};
long encoderFullTurn[2] = {ENCODER1_RATIO, ENCODER2_RATIO};
long steppersPos[6] = {0, 0, 0, 0, 0, 0};

AccelStepper newStepper(int stepPin, int dirPin, int maxSpeed, bool inverted){
  AccelStepper stepper = AccelStepper(stepper.DRIVER, stepPin, dirPin);
  stepper.setPinsInverted(inverted, inverted, false);
  stepper.setMaxSpeed(maxSpeed);
  stepper.setAcceleration(4000);
  stepper.enableOutputs();

  return stepper;
}

IRAM_ATTR void encoder1Position()
{
  encoder1->tick(); // just call tick() to check the state.
}

// IRAM_ATTR void encoder2Position()
// {
//   // encoder2->tick(); // just call tick() to check the state.
// }


void robot_arm_cmd_callback(const robot_arm_hardware::RobotArmCmd& cmd){
    
      moveDegrees(0, -(cmd.pos[0]));
      moveDegrees(1, (cmd.pos[1]));      
      moveDegrees(2, -(cmd.pos[2]));
      moveDegrees(3, -(cmd.pos[3]));
      moveDegrees(4, -(cmd.pos[4]));
      moveDegrees(5, -(cmd.pos[5]));
      
    
}

ros::Subscriber<robot_arm_hardware::RobotArmCmd> robot_arm_cmd_sub("/robot_arm/cmd", &robot_arm_cmd_callback);


void setup() {

  if (!ROS_SERIAL){
    Serial.begin(115200);
  }  else {
    nh.getHardware()->setBaud(115200);
    nh.initNode();            
    nh.advertise(robot_arm_state_pub);
    nh.subscribe(robot_arm_cmd_sub);
  }
  

  // put your setup code here, to run once:
  steppers[0] = newStepper(MOTOR1_STEP, MOTOR1_DIR, MOTOR1_MAXSPEED, true);
  steppers[1] = newStepper(MOTOR2_STEP, MOTOR2_DIR, MOTOR2_MAXSPEED, true);
  steppers[2] = newStepper(MOTOR3_STEP, MOTOR3_DIR, MOTOR3_MAXSPEED, true);
  steppers[3] = newStepper(MOTOR4_STEP, MOTOR4_DIR, MOTOR4_MAXSPEED, true);
  steppers[4] = newStepper(MOTOR5_STEP, MOTOR5_DIR, MOTOR5_MAXSPEED, true);
  steppers[5] = newStepper(MOTOR6_STEP, MOTOR6_DIR, MOTOR6_MAXSPEED, true);
  msteppers.addStepper(steppers[0]);
  msteppers.addStepper(steppers[1]);
  msteppers.addStepper(steppers[2]);
  msteppers.addStepper(steppers[3]);
  msteppers.addStepper(steppers[4]);
  msteppers.addStepper(steppers[5]);
  encoder1 = new RotaryEncoder(ENCODER1_PINA, ENCODER1_PINB, RotaryEncoder::LatchMode::TWO03);
  // encoder2 = new RotaryEncoder(ENCODER2_PINA, ENCODER2_PINB, RotaryEncoder::LatchMode::TWO03);

  attachInterrupt(digitalPinToInterrupt(ENCODER1_PINA), encoder1Position, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER1_PINB), encoder1Position, CHANGE);

  // attachInterrupt(digitalPinToInterrupt(ENCODER2_PINA), encoder2Position, CHANGE);
  // attachInterrupt(digitalPinToInterrupt(ENCODER2_PINB), encoder2Position, CHANGE);


  // encoder1->setPosition(0);
  // encoder2->setPosition(0);

  //  Serial.print(encoder1->getPosition());    

  // initPos();
}

void runSteppers(){
  msteppers.run();
}


void moveDegrees(int stepper, double degree){ 
  double steps = stepperFullTurn[stepper] * degree / 360;    

  steppersPos[stepper] = long(steps);
}


double stepsToDegree(int stepper, long steps){
  double degree = ((double)steps / (double)stepperFullTurn[stepper]) * 360.0; 

  return degree;   
}


long tempStepperPos = 0;
double tempEncoderPos = 0;

int isInit = 0;
int initDone = 0;


void initPos(){
  isInit = 1;
  initDone = 0;
  moveDegrees(1, 55);
  moveDegrees(2, -87);  
  msteppers.moveTo(steppersPos);
  msteppers.runSpeedToPosition();
  
  steppers[1].setCurrentPosition(0);
  steppers[2].setCurrentPosition(0);
  moveDegrees(1, 0);
  moveDegrees(2, 0);  
  isInit = 0;
}


unsigned long delaytime = millis();
void loop() {

  if (ROS_SERIAL) {
    nh.spinOnce();
  } else {
    readCommand();
  }

  if (isInit == 0){
    long stepper1CurrentPos = steppers[0].currentPosition();
    long encoder1CurrentPos = encoder1->getPosition() ;
    
    double encoder1Angle = encoder1CurrentPos *  360.0 /ENCODER1_RATIO;
    double encoder1Pos = long(encoder1Angle *  stepperFullTurn[0] /360.0);

    // Serial.print(stepper1CurrentPos);
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

     msteppers.moveTo(steppersPos);
     msteppers.runSpeedToPosition();
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
  }
    
    // steppers[1].moveTo(steppersPos[1]);
    // steppers[2].moveTo(steppersPos[2]);
    // steppers[3].moveTo(steppersPos[3]);     
    delay(1);    
  }
  // encoder1->tick();
  // encoder2->tick();

           
    
}

void readCommand(){
  if (Serial.available()){
    Serial.println(MOTOR1_RATIO);    
    String command = Serial.readStringUntil('\n');
    
    int index = command.indexOf(',');
    double degree = command.substring(0, index).toDouble();
    command = command.substring(index + 1);
    moveDegrees(0, degree);

    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();    
    command = command.substring(index + 1);
    moveDegrees(1, degree);
    
    
    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();        
    command = command.substring(index + 1);  
    moveDegrees(2, degree);
    

    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();        
    command = command.substring(index + 1);
    Serial.println(degree);
    moveDegrees(3, degree);


    index = command.indexOf(',');
    degree = command.substring(0, index).toDouble();        
    command = command.substring(index + 1);
    Serial.println(degree);
    moveDegrees(4, degree);    
    
    degree = command.toDouble();  
    moveDegrees(5, degree);
  
    // steppers[0].setCurrentPosition(stepper1CurrentPos);
    // steppers[0].moveTo(steppersPos[0]);
    // steppers[1].moveTo(steppersPos[1]);
    // steppers[2].moveTo(steppersPos[2]);
    // steppers[3].moveTo(steppersPos[3]);
    
  }

}

void publish_robot_state(){

  robotArmState.pos[0] = -(stepsToDegree(0, steppers[0].currentPosition())); 
  robotArmState.pos[1] = (stepsToDegree(1, steppers[1].currentPosition())); 
  robotArmState.pos[2] = -(stepsToDegree(2, steppers[2].currentPosition())); 
  robotArmState.pos[3] = -(stepsToDegree(3, steppers[3].currentPosition())); 
  robotArmState.pos[4] = -(stepsToDegree(4, steppers[4].currentPosition())); 
  robotArmState.pos[5] = -(stepsToDegree(5, steppers[5].currentPosition())); 

  
  robot_arm_state_pub.publish(&robotArmState);
}

