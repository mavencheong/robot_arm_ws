;; Auto-generated. Do not edit!


(when (boundp 'robot_arm_hardware::RobotArmCmd)
  (if (not (find-package "ROBOT_ARM_HARDWARE"))
    (make-package "ROBOT_ARM_HARDWARE"))
  (shadow 'RobotArmCmd (find-package "ROBOT_ARM_HARDWARE")))
(unless (find-package "ROBOT_ARM_HARDWARE::ROBOTARMCMD")
  (make-package "ROBOT_ARM_HARDWARE::ROBOTARMCMD"))

(in-package "ROS")
;;//! \htmlinclude RobotArmCmd.msg.html


(defclass robot_arm_hardware::RobotArmCmd
  :super ros::object
  :slots (_vel _pos ))

(defmethod robot_arm_hardware::RobotArmCmd
  (:init
   (&key
    ((:vel __vel) (make-array 8 :initial-element 0.0 :element-type :float))
    ((:pos __pos) (make-array 8 :initial-element 0.0 :element-type :float))
    )
   (send-super :init)
   (setq _vel __vel)
   (setq _pos __pos)
   self)
  (:vel
   (&optional __vel)
   (if __vel (setq _vel __vel)) _vel)
  (:pos
   (&optional __pos)
   (if __pos (setq _pos __pos)) _pos)
  (:serialization-length
   ()
   (+
    ;; float32[8] _vel
    (* 4    8)
    ;; float32[8] _pos
    (* 4    8)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; float32[8] _vel
     (dotimes (i 8)
       (sys::poke (elt _vel i) (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
       )
     ;; float32[8] _pos
     (dotimes (i 8)
       (sys::poke (elt _pos i) (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; float32[8] _vel
   (dotimes (i (length _vel))
     (setf (elt _vel i) (sys::peek buf ptr- :float)) (incf ptr- 4)
     )
   ;; float32[8] _pos
   (dotimes (i (length _pos))
     (setf (elt _pos i) (sys::peek buf ptr- :float)) (incf ptr- 4)
     )
   ;;
   self)
  )

(setf (get robot_arm_hardware::RobotArmCmd :md5sum-) "3d18602b275ad29bfcdcebe549a29615")
(setf (get robot_arm_hardware::RobotArmCmd :datatype-) "robot_arm_hardware/RobotArmCmd")
(setf (get robot_arm_hardware::RobotArmCmd :definition-)
      "float32[8] vel #actuator vel
float32[8] pos #actuator position
")



(provide :robot_arm_hardware/RobotArmCmd "3d18602b275ad29bfcdcebe549a29615")


