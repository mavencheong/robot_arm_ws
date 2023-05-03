#!/usr/bin/env python

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import sensor_msgs.msg
import std_msgs.msg
import geometry_msgs.msg

from std_msgs.msg import Header
from moveit_msgs.msg import RobotState
from sensor_msgs.msg import JointState
from tf.transformations import quaternion_from_euler

def setStartState(arm):
   print("============ Set Start State")
  #  joint_state = JointState()
  #  joint_state.header = Header()
  #  joint_state.header.stamp = rospy.Time.now()
  #  joint_state.name = ["joint_2", "joint_3"]
  #  joint_state.position = [-0.8726, -1.5507]


  #  robot_state = RobotState()
  #  robot_state.joint_state = joint_state

  #  arm.set_start_state(robot_state)





def goToHome(arm):
   print("============ Set Home Pose")
   
   arm.set_named_target("home")
   plan = arm.plan()
   rospy.sleep(2)
   arm.go(wait=True)

def goInitPos(arm):
   print("============ Set Init Pose")
   arm.set_named_target("initial")
   plan = arm.plan()
   rospy.sleep(2)
   arm.go(wait=True)

   

def goStraightPos(arm):
   print("============ Set Straight Pose")
   arm.set_named_target("straight")
   plan = arm.plan()
   rospy.sleep(2)
   arm.go(wait=True)

def goStretchPos(arm):
   print("============ Set Stretch Pose")
   arm.set_named_target("stretch")
   plan = arm.plan()
   rospy.sleep(5)
   arm.go(wait=True)


def main():
    
    print("============ Starting tutorial setup")

    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('move_group_python_interface_tutorial',
                  anonymous=True)

    ## Instantiate a RobotCommander object.  This object is an interface to
    ## the robot as a whole.
    robot = moveit_commander.RobotCommander()

    ## Instantiate a PlanningSceneInterface object.  This object is an interface
    ## to the world surrounding the robot.
    scene = moveit_commander.PlanningSceneInterface()

    arm = moveit_commander.MoveGroupCommander("arm")

    print("============ Printing robot state")
    print(robot.get_current_state())
    print("============")

    goInitPos(arm)
    rospy.sleep(12)
    goToHome(arm)
    rospy.sleep(12)



    # setStartState(arm)
    # rospy.sleep(5)

   #  goToHome(arm)
   #  rospy.sleep(12)

   #  goInitPos(arm)
   #  rospy.sleep(12)

    goStraightPos(arm)
    rospy.sleep(12)

    goStretchPos(arm)
    rospy.sleep(12)
    
    goInitPos(arm)
    rospy.sleep(12)
    ## When finished shut down moveit_commander.
    moveit_commander.roscpp_shutdown()

    ## END_TUTORIAL

    print("============ STOPPING")


if __name__=='__main__':
  try:
    main()
  
  except rospy.ROSInterruptException:
    pass