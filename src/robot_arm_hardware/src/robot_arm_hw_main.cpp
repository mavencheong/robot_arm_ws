
#include <generic_hw_control_loop.h>
#include <robot_arm_hw_interface.h>

int main(int argc, char **argv) {
  ros::init(argc, argv, "robot_arm_hw_interface");
  ros::NodeHandle nh;

  // NOTE: We run the ROS loop in a separate thread as external calls such
  // as service callbacks to load controllers can block the (main) control loop
  ros::AsyncSpinner spinner(3);
  spinner.start();

  // Create the hardware interface specific to your robot
  std::shared_ptr<robot_arm_ns::RobotArmHWInterface> robot_arm_hw_interface(
      new robot_arm_ns::RobotArmHWInterface(nh));
  robot_arm_hw_interface->init();

  // Start the control loop
  ros_control_boilerplate::GenericHWControlLoop control_loop(
      nh, robot_arm_hw_interface);

  control_loop.run(); // Blocks until shutdown signal recieved

  return 0;
}
