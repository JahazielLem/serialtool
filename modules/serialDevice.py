import serial
import time
DEFAULT_BAUDRATE = 115200
DEFAULT_CRLF = "\n"


class SerialError(Exception):
  pass

class SerialPort:
  def __init__(self):
    self.serial_device = serial.Serial()
    self.serial_device.baudrate = DEFAULT_BAUDRATE
    self.serial_alive = True
  
  def set_serial_port(self, port):
    self.serial_device.port = port
  
  def set_baudrate(self, baudrate):
    if baudrate not in serial.Serial.BAUDRATES:
      raise ValueError("Invalid baudrate")
    self.serial_device.baudrate = baudrate
  
  def get_port(self):
    return self.serial_device.port
  
  def is_connected(self):
    return self.serial_device.is_open

  def resetBuffer(self):
    self.serial_device.reset_input_buffer()
    self.serial_device.reset_output_buffer()

  def open(self):
    try:
      if not self.is_connected():
        self.serial_device.open()
        self.resetBuffer()
        self.serial_alive = True
    except serial.SerialException as e:
      raise SerialError(e)
  
  def close(self):
    if self.is_connected():
      try:
        self.serial_device.close()
        self.serial_alive = False
      except serial.SerialException as e:
        raise SerialError(e)
  
  def recv(self):
    try:
      bytestream = self.serial_device.readline().decode().strip()
      return bytestream
    except serial.SerialException as e:
      self.serial_alive = False
  
  def transmit(self, data):
    message = f"{data}\r\n"
    self.serial_device.write(message.encode())
  
  def reconnect(self):
    while not self.serial_alive:
      time.sleep(3)
      self.open()