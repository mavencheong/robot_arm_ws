# generated from catkin/cmake/template/pkg.context.pc.in
CATKIN_PACKAGE_PREFIX = ""
PROJECT_PKG_CONFIG_INCLUDE_DIRS = "${prefix}/include".split(';') if "${prefix}/include" != "" else []
PROJECT_CATKIN_DEPENDS = "moveit_core;moveit_task_constructor_msgs;roscpp;rviz".replace(';', ' ')
PKG_CONFIG_LIBRARIES_WITH_PREFIX = "-lmoveit_task_visualization_tools;-lmotion_planning_tasks_utils".split(';') if "-lmoveit_task_visualization_tools;-lmotion_planning_tasks_utils" != "" else []
PROJECT_NAME = "moveit_task_constructor_visualization"
PROJECT_SPACE_DIR = "/home/maven/robot_arm_ws/install"
PROJECT_VERSION = "0.1.3"
