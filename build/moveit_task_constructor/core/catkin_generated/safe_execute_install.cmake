execute_process(COMMAND "/home/maven/robot_arm_ws/build/moveit_task_constructor/core/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/maven/robot_arm_ws/build/moveit_task_constructor/core/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
