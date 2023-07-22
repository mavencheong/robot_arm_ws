
(cl:in-package :asdf)

(defsystem "robot_arm_hardware-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "RobotArmCmd" :depends-on ("_package_RobotArmCmd"))
    (:file "_package_RobotArmCmd" :depends-on ("_package"))
    (:file "RobotArmState" :depends-on ("_package_RobotArmState"))
    (:file "_package_RobotArmState" :depends-on ("_package"))
  ))