;; Auto-generated. Do not edit!


(when (boundp 'robot_arm_hardware::RobotArmState)
  (if (not (find-package "ROBOT_ARM_HARDWARE"))
    (make-package "ROBOT_ARM_HARDWARE"))
  (shadow 'RobotArmState (find-package "ROBOT_ARM_HARDWARE")))
(unless (find-package "ROBOT_ARM_HARDWARE::ROBOTARMSTATE")
  (make-package "ROBOT_ARM_HARDWARE::ROBOTARMSTATE"))

(in-package "ROS")
;;//! \htmlinclude RobotArmState.msg.html


(defclass robot_arm_hardware::RobotArmState
  :super ros::object
  :slots (_vel _pos _encoder ))

(defmethod robot_arm_hardware::RobotArmState
  (:init
   (&key
    ((:vel __vel) (make-array 9 :initial-element 0.0 :element-type :float))
    ((:pos __pos) (make-array 8 :initial-element 0.0 :element-type :float))
    ((:encoder __encoder) (make-array 8 :initial-element 0.0 :element-type :float))
    )
   (send-super :init)
   (setq _vel __vel)
   (setq _pos __pos)
   (setq _encoder __encoder)
   self)
  (:vel
   (&optional __vel)
   (if __vel (setq _vel __vel)) _vel)
  (:pos
   (&optional __pos)
   (if __pos (setq _pos __pos)) _pos)
  (:encoder
   (&optional __encoder)
   (if __encoder (setq _encoder __encoder)) _encoder)
  (:serialization-length
   ()
   (+
    ;; float32[9] _vel
    (* 4    9)
    ;; float32[8] _pos
    (* 4    8)
    ;; float32[8] _encoder
    (* 4    8)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; float32[9] _vel
     (dotimes (i 9)
       (sys::poke (elt _vel i) (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
       )
     ;; float32[8] _pos
     (dotimes (i 8)
       (sys::poke (elt _pos i) (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
       )
     ;; float32[8] _encoder
     (dotimes (i 8)
       (sys::poke (elt _encoder i) (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; float32[9] _vel
   (dotimes (i (length _vel))
     (setf (elt _vel i) (sys::peek buf ptr- :float)) (incf ptr- 4)
     )
   ;; float32[8] _pos
   (dotimes (i (length _pos))
     (setf (elt _pos i) (sys::peek buf ptr- :float)) (incf ptr- 4)
     )
   ;; float32[8] _encoder
   (dotimes (i (length _encoder))
     (setf (elt _encoder i) (sys::peek buf ptr- :float)) (incf ptr- 4)
     )
   ;;
   self)
  )

(setf (get robot_arm_hardware::RobotArmState :md5sum-) "d53385e21754d4b8e3401e31a5f53cfc")
(setf (get robot_arm_hardware::RobotArmState :datatype-) "robot_arm_hardware/RobotArmState")
(setf (get robot_arm_hardware::RobotArmState :definition-)
      "float32[9] vel # actuator vel
float32[8] pos #position in degree
float32[8] encoder #encoder
")



(provide :robot_arm_hardware/RobotArmState "d53385e21754d4b8e3401e31a5f53cfc")


