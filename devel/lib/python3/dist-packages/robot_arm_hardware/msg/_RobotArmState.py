# This Python file uses the following encoding: utf-8
"""autogenerated by genpy from robot_arm_hardware/RobotArmState.msg. Do not edit."""
import codecs
import sys
python3 = True if sys.hexversion > 0x03000000 else False
import genpy
import struct


class RobotArmState(genpy.Message):
  _md5sum = "d53385e21754d4b8e3401e31a5f53cfc"
  _type = "robot_arm_hardware/RobotArmState"
  _has_header = False  # flag to mark the presence of a Header object
  _full_text = """float32[9] vel # actuator vel
float32[8] pos #position in degree
float32[8] encoder #encoder"""
  __slots__ = ['vel','pos','encoder']
  _slot_types = ['float32[9]','float32[8]','float32[8]']

  def __init__(self, *args, **kwds):
    """
    Constructor. Any message fields that are implicitly/explicitly
    set to None will be assigned a default value. The recommend
    use is keyword arguments as this is more robust to future message
    changes.  You cannot mix in-order arguments and keyword arguments.

    The available fields are:
       vel,pos,encoder

    :param args: complete set of field values, in .msg order
    :param kwds: use keyword arguments corresponding to message field names
    to set specific fields.
    """
    if args or kwds:
      super(RobotArmState, self).__init__(*args, **kwds)
      # message fields cannot be None, assign default values for those that are
      if self.vel is None:
        self.vel = [0.] * 9
      if self.pos is None:
        self.pos = [0.] * 8
      if self.encoder is None:
        self.encoder = [0.] * 8
    else:
      self.vel = [0.] * 9
      self.pos = [0.] * 8
      self.encoder = [0.] * 8

  def _get_types(self):
    """
    internal API method
    """
    return self._slot_types

  def serialize(self, buff):
    """
    serialize message into buffer
    :param buff: buffer, ``StringIO``
    """
    try:
      buff.write(_get_struct_9f().pack(*self.vel))
      buff.write(_get_struct_8f().pack(*self.pos))
      buff.write(_get_struct_8f().pack(*self.encoder))
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize(self, str):
    """
    unpack serialized message in str into this message instance
    :param str: byte array of serialized message, ``str``
    """
    if python3:
      codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      end = 0
      start = end
      end += 36
      self.vel = _get_struct_9f().unpack(str[start:end])
      start = end
      end += 32
      self.pos = _get_struct_8f().unpack(str[start:end])
      start = end
      end += 32
      self.encoder = _get_struct_8f().unpack(str[start:end])
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill


  def serialize_numpy(self, buff, numpy):
    """
    serialize message with numpy array types into buffer
    :param buff: buffer, ``StringIO``
    :param numpy: numpy python module
    """
    try:
      buff.write(self.vel.tostring())
      buff.write(self.pos.tostring())
      buff.write(self.encoder.tostring())
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize_numpy(self, str, numpy):
    """
    unpack serialized message in str into this message instance using numpy for array types
    :param str: byte array of serialized message, ``str``
    :param numpy: numpy python module
    """
    if python3:
      codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      end = 0
      start = end
      end += 36
      self.vel = numpy.frombuffer(str[start:end], dtype=numpy.float32, count=9)
      start = end
      end += 32
      self.pos = numpy.frombuffer(str[start:end], dtype=numpy.float32, count=8)
      start = end
      end += 32
      self.encoder = numpy.frombuffer(str[start:end], dtype=numpy.float32, count=8)
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill

_struct_I = genpy.struct_I
def _get_struct_I():
    global _struct_I
    return _struct_I
_struct_8f = None
def _get_struct_8f():
    global _struct_8f
    if _struct_8f is None:
        _struct_8f = struct.Struct("<8f")
    return _struct_8f
_struct_9f = None
def _get_struct_9f():
    global _struct_9f
    if _struct_9f is None:
        _struct_9f = struct.Struct("<9f")
    return _struct_9f