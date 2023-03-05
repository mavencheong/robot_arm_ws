

#include <robot_arm_hw_interface.h>
// ROS parameter loading
#include <rosparam_shortcuts/rosparam_shortcuts.h>

namespace robot_arm_ns
{
  RobotArmHWInterface::RobotArmHWInterface(ros::NodeHandle &nh,
                                       urdf::Model *urdf_model)
      : ros_control_boilerplate::GenericHWInterface(nh, urdf_model)
  {
    // Load rosparams

    robot_arm_state_sub = nh.subscribe("/robot_arm/state", 1,
                                   &RobotArmHWInterface::stateCallback, this);


    // wheel_encoder_sub = nh.subscribe("/vacumm/wheel_encoder", 1,
    //                                &VacummHWInterface::wheelEncoderCallback, this);


    robot_arm_cmd_pub = nh.advertise<robot_arm_hardware::RobotArmCmd>("/robot_arm/cmd", 3);
    ros::NodeHandle rpnh(nh_, "hardware_interface");

    double robtArmVel[num_joints_];
  }

  void RobotArmHWInterface::stateCallback(
      const robot_arm_hardware::RobotArmState::ConstPtr &msg)
  {
    double angles[num_joints_];
    double degrees[num_joints_];
    double angles_delta[num_joints_];
    for (int i = 0; i < num_joints_; i++)
    {
      degrees[i] = msg->pos[i];
      angles[i] = degreeToAngles(degrees[i]);

      angles_delta[i] = angles[i] - joint_position_[i];  

      joint_velocity_[i] = msg->vel[i];
      joint_position_[i] = angles[i] ;
    }
  }


  void RobotArmHWInterface::init()
  {
    // Call parent class version of this function
    GenericHWInterface::init();

    ROS_INFO("RobotArmHWInterface Ready.");
  }

  void RobotArmHWInterface::read(ros::Duration &elapsed_time)
  {

  }

  void RobotArmHWInterface::write(ros::Duration &elapsed_time)
  {
    // Safety
    
    enforceLimits(elapsed_time);


    static robot_arm_hardware::RobotArmCmd cmd;
    const double cmd_dt(elapsed_time.toSec());
    
    for (int i = 0; i < num_joints_; i++)
    {
      cmd.vel[i] = joint_velocity_command_[i];
      cmd.pos[i] = angleToDegree(joint_position_command_[i]);

    //   joint_velocity_[i] = joint_velocity_command_[i];
    // joint_position_[i] = joint_position_command_[i];


      // ROS_INFO_STREAM_NAMED(
      //     name_, "Velocity" << joint_velocity_command_[i]  << ", Elapsed Time: " << cmd_dt << "Position: " << joint_position_[i]  );
    }
    // printCommand();
    robot_arm_cmd_pub.publish(cmd);
  }

  void RobotArmHWInterface::enforceLimits(ros::Duration &period)
  {
    // Enforces position and velocity
    pos_jnt_sat_interface_.enforceLimits(period);
  }

  

  double RobotArmHWInterface::degreeToAngles(const double &degree)
  {
    return degree * M_PI / 180;
  }


  double RobotArmHWInterface::angleToDegree(const double angle)
  {
    return angle * 180 / M_PI;
  }

} // namespace vacumm_ns