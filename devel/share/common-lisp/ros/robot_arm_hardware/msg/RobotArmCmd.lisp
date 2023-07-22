; Auto-generated. Do not edit!


(cl:in-package robot_arm_hardware-msg)


;//! \htmlinclude RobotArmCmd.msg.html

(cl:defclass <RobotArmCmd> (roslisp-msg-protocol:ros-message)
  ((vel
    :reader vel
    :initarg :vel
    :type (cl:vector cl:float)
   :initform (cl:make-array 8 :element-type 'cl:float :initial-element 0.0))
   (pos
    :reader pos
    :initarg :pos
    :type (cl:vector cl:float)
   :initform (cl:make-array 8 :element-type 'cl:float :initial-element 0.0)))
)

(cl:defclass RobotArmCmd (<RobotArmCmd>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <RobotArmCmd>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'RobotArmCmd)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name robot_arm_hardware-msg:<RobotArmCmd> is deprecated: use robot_arm_hardware-msg:RobotArmCmd instead.")))

(cl:ensure-generic-function 'vel-val :lambda-list '(m))
(cl:defmethod vel-val ((m <RobotArmCmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader robot_arm_hardware-msg:vel-val is deprecated.  Use robot_arm_hardware-msg:vel instead.")
  (vel m))

(cl:ensure-generic-function 'pos-val :lambda-list '(m))
(cl:defmethod pos-val ((m <RobotArmCmd>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader robot_arm_hardware-msg:pos-val is deprecated.  Use robot_arm_hardware-msg:pos instead.")
  (pos m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <RobotArmCmd>) ostream)
  "Serializes a message object of type '<RobotArmCmd>"
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let ((bits (roslisp-utils:encode-single-float-bits ele)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)))
   (cl:slot-value msg 'vel))
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let ((bits (roslisp-utils:encode-single-float-bits ele)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)))
   (cl:slot-value msg 'pos))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <RobotArmCmd>) istream)
  "Deserializes a message object of type '<RobotArmCmd>"
  (cl:setf (cl:slot-value msg 'vel) (cl:make-array 8))
  (cl:let ((vals (cl:slot-value msg 'vel)))
    (cl:dotimes (i 8)
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:aref vals i) (roslisp-utils:decode-single-float-bits bits)))))
  (cl:setf (cl:slot-value msg 'pos) (cl:make-array 8))
  (cl:let ((vals (cl:slot-value msg 'pos)))
    (cl:dotimes (i 8)
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:aref vals i) (roslisp-utils:decode-single-float-bits bits)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<RobotArmCmd>)))
  "Returns string type for a message object of type '<RobotArmCmd>"
  "robot_arm_hardware/RobotArmCmd")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'RobotArmCmd)))
  "Returns string type for a message object of type 'RobotArmCmd"
  "robot_arm_hardware/RobotArmCmd")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<RobotArmCmd>)))
  "Returns md5sum for a message object of type '<RobotArmCmd>"
  "3d18602b275ad29bfcdcebe549a29615")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'RobotArmCmd)))
  "Returns md5sum for a message object of type 'RobotArmCmd"
  "3d18602b275ad29bfcdcebe549a29615")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<RobotArmCmd>)))
  "Returns full string definition for message of type '<RobotArmCmd>"
  (cl:format cl:nil "float32[8] vel #actuator vel~%float32[8] pos #actuator position~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'RobotArmCmd)))
  "Returns full string definition for message of type 'RobotArmCmd"
  (cl:format cl:nil "float32[8] vel #actuator vel~%float32[8] pos #actuator position~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <RobotArmCmd>))
  (cl:+ 0
     0 (cl:reduce #'cl:+ (cl:slot-value msg 'vel) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
     0 (cl:reduce #'cl:+ (cl:slot-value msg 'pos) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <RobotArmCmd>))
  "Converts a ROS message object to a list"
  (cl:list 'RobotArmCmd
    (cl:cons ':vel (vel msg))
    (cl:cons ':pos (pos msg))
))
