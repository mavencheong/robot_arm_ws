// Auto-generated. Do not edit!

// (in-package robot_arm_hardware.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class RobotArmState {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.vel = null;
      this.pos = null;
      this.encoder = null;
    }
    else {
      if (initObj.hasOwnProperty('vel')) {
        this.vel = initObj.vel
      }
      else {
        this.vel = new Array(9).fill(0);
      }
      if (initObj.hasOwnProperty('pos')) {
        this.pos = initObj.pos
      }
      else {
        this.pos = new Array(8).fill(0);
      }
      if (initObj.hasOwnProperty('encoder')) {
        this.encoder = initObj.encoder
      }
      else {
        this.encoder = new Array(8).fill(0);
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type RobotArmState
    // Check that the constant length array field [vel] has the right length
    if (obj.vel.length !== 9) {
      throw new Error('Unable to serialize array field vel - length must be 9')
    }
    // Serialize message field [vel]
    bufferOffset = _arraySerializer.float32(obj.vel, buffer, bufferOffset, 9);
    // Check that the constant length array field [pos] has the right length
    if (obj.pos.length !== 8) {
      throw new Error('Unable to serialize array field pos - length must be 8')
    }
    // Serialize message field [pos]
    bufferOffset = _arraySerializer.float32(obj.pos, buffer, bufferOffset, 8);
    // Check that the constant length array field [encoder] has the right length
    if (obj.encoder.length !== 8) {
      throw new Error('Unable to serialize array field encoder - length must be 8')
    }
    // Serialize message field [encoder]
    bufferOffset = _arraySerializer.float32(obj.encoder, buffer, bufferOffset, 8);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type RobotArmState
    let len;
    let data = new RobotArmState(null);
    // Deserialize message field [vel]
    data.vel = _arrayDeserializer.float32(buffer, bufferOffset, 9)
    // Deserialize message field [pos]
    data.pos = _arrayDeserializer.float32(buffer, bufferOffset, 8)
    // Deserialize message field [encoder]
    data.encoder = _arrayDeserializer.float32(buffer, bufferOffset, 8)
    return data;
  }

  static getMessageSize(object) {
    return 100;
  }

  static datatype() {
    // Returns string type for a message object
    return 'robot_arm_hardware/RobotArmState';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'd53385e21754d4b8e3401e31a5f53cfc';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    float32[9] vel # actuator vel
    float32[8] pos #position in degree
    float32[8] encoder #encoder
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new RobotArmState(null);
    if (msg.vel !== undefined) {
      resolved.vel = msg.vel;
    }
    else {
      resolved.vel = new Array(9).fill(0)
    }

    if (msg.pos !== undefined) {
      resolved.pos = msg.pos;
    }
    else {
      resolved.pos = new Array(8).fill(0)
    }

    if (msg.encoder !== undefined) {
      resolved.encoder = msg.encoder;
    }
    else {
      resolved.encoder = new Array(8).fill(0)
    }

    return resolved;
    }
};

module.exports = RobotArmState;
