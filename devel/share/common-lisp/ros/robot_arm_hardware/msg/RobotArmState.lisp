; Auto-generated. Do not edit!


(cl:in-package robot_arm_hardware-msg)


;//! \htmlinclude RobotArmState.msg.html

(cl:defclass <RobotArmState> (roslisp-msg-protocol:ros-message)
  ((vel
    :reader vel
    :initarg :vel
    :type (cl:vector cl:float)
   :initform (cl:make-array 9 :element-type 'cl:float :initial-element 0.0))
   (pos
    :reader pos
    :initarg :pos
    :type (cl:vector cl:float)
   :initform (cl:make-array 8 :element-type 'cl:float :initial-element 0.0))
   (encoder
    :reader encoder
    :initarg :encoder
    :type (cl:vector cl:float)
   :initform (cl:make-array 8 :element-type 'cl:float :initial-element 0.0)))
)

(cl:defclass RobotArmState (<RobotArmState>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <RobotArmState>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'RobotArmState)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name robot_arm_hardware-msg:<RobotArmState> is deprecated: use robot_arm_hardware-msg:RobotArmState instead.")))

(cl:ensure-generic-function 'vel-val :lambda-list '(m))
(cl:defmethod vel-val ((m <RobotArmState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader robot_arm_hardware-msg:vel-val is deprecated.  Use robot_arm_hardware-msg:vel instead.")
  (vel m))

(cl:ensure-generic-function 'pos-val :lambda-list '(m))
(cl:defmethod pos-val ((m <RobotArmState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader robot_arm_hardware-msg:pos-val is deprecated.  Use robot_arm_hardware-msg:pos instead.")
  (pos m))

(cl:ensure-generic-function 'encoder-val :lambda-list '(m))
(cl:defmethod encoder-val ((m <RobotArmState>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader robot_arm_hardware-msg:encoder-val is deprecated.  Use robot_arm_hardware-msg:encoder instead.")
  (encoder m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <RobotArmState>) ostream)
  "Serializes a message object of type '<RobotArmState>"
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
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let ((bits (roslisp-utils:encode-single-float-bits ele)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)))
   (cl:slot-value msg 'encoder))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <RobotArmState>) istream)
  "Deserializes a message object of type '<RobotArmState>"
  (cl:setf (cl:slot-value msg 'vel) (cl:make-array 9))
  (cl:let ((vals (cl:slot-value msg 'vel)))
    (cl:dotimes (i 9)
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
  (cl:setf (cl:slot-value msg 'encoder) (cl:make-array 8))
  (cl:let ((vals (cl:slot-value msg 'encoder)))
    (cl:dotimes (i 8)
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:aref vals i) (roslisp-utils:decode-single-float-bits bits)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<RobotArmState>)))
  "Returns string type for a message object of type '<RobotArmState>"
  "robot_arm_hardware/RobotArmState")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'RobotArmState)))
  "Returns string type for a message object of type 'RobotArmState"
  "robot_arm_hardware/RobotArmState")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<RobotArmState>)))
  "Returns md5sum for a message object of type '<RobotArmState>"
  "d53385e21754d4b8e3401e31a5f53cfc")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'RobotArmState)))
  "Returns md5sum for a message object of type 'RobotArmState"
  "d53385e21754d4b8e3401e31a5f53cfc")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<RobotArmState>)))
  "Returns full string definition for message of type '<RobotArmState>"
  (cl:format cl:nil "float32[9] vel # actuator vel~%float32[8] pos #position in degree~%float32[8] encoder #encoder~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'RobotArmState)))
  "Returns full string definition for message of type 'RobotArmState"
  (cl:format cl:nil "float32[9] vel # actuator vel~%float32[8] pos #position in degree~%float32[8] encoder #encoder~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <RobotArmState>))
  (cl:+ 0
     0 (cl:reduce #'cl:+ (cl:slot-value msg 'vel) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
     0 (cl:reduce #'cl:+ (cl:slot-value msg 'pos) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
     0 (cl:reduce #'cl:+ (cl:slot-value msg 'encoder) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <RobotArmState>))
  "Converts a ROS message object to a list"
  (cl:list 'RobotArmState
    (cl:cons ':vel (vel msg))
    (cl:cons ':pos (pos msg))
    (cl:cons ':encoder (encoder msg))
))
