# generated from catkin/cmake/template/pkg.context.pc.in
CATKIN_PACKAGE_PREFIX = ""
PROJECT_PKG_CONFIG_INCLUDE_DIRS = "${prefix}/include".split(';') if "${prefix}/include" != "" else []
PROJECT_CATKIN_DEPENDS = "geometry_msgs;moveit_core;moveit_task_constructor_msgs;rviz_marker_tools;visualization_msgs".replace(';', ' ')
PKG_CONFIG_LIBRARIES_WITH_PREFIX = "-lmoveit_task_constructor_core;-lmoveit_task_constructor_core_stages;-lmoveit_task_constructor_core_stage_plugins".split(';') if "-lmoveit_task_constructor_core;-lmoveit_task_constructor_core_stages;-lmoveit_task_constructor_core_stage_plugins" != "" else []
PROJECT_NAME = "moveit_task_constructor_core"
PROJECT_SPACE_DIR = "/home/maven/robot_arm_ws/install"
PROJECT_VERSION = "0.1.3"
