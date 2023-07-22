#ifndef ROBOT_ARM_HW_INTERFACE_H
#define ROBOT_ARM_HW_INTERFACE_H

#include <generic_hw_interface.h>
#include <robot_arm_hardware/RobotArmCmd.h>
#include <robot_arm_hardware/RobotArmState.h>

namespace robot_arm_ns {
/** \brief Hardware interface for a robot */
class RobotArmHWInterface : public ros_control_boilerplate::GenericHWInterface {
public:
  /**
   * \brief Constructor
   * \param nh - Node handle for topics.
   */
  RobotArmHWInterface(ros::NodeHandle &nh, urdf::Model *urdf_model = NULL);

  /** \brief Initialize the robot hardware interface */
  virtual void init();

  /** \brief Read the state from the robot hardware. */
  virtual void read(ros::Duration &elapsed_time);

  /** \brief Write the command to the robot hardware. */
  virtual void write(ros::Duration &elapsed_time);

  /** \breif Enforce limits for all values before writing */
  virtual void enforceLimits(ros::Duration &period);

protected:
  ros::Subscriber robot_arm_state_sub;
  ros::Publisher robot_arm_cmd_pub;
  
  void stateCallback(const robot_arm_hardware::RobotArmState::ConstPtr &msg);

  double angleToDegree(const double angle);
  double degreeToAngles(const double &degree);
}; // class

} // namespace vacumm_ns

#endif