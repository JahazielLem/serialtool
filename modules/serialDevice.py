import serial
import time
import chardet

DEFAULT_BAUDRATE = 115200
DEFAULT_CRLF = "\n"

class SerialError(Exception):
  pass

class SerialPort:
  def __init__(self):
      self.serial_device = serial.Serial()
      self.serial_device.baudrate = DEFAULT_BAUDRATE
      self.serial_alive = False

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

  def reset_buffer(self):
      self.serial_device.reset_input_buffer()
      self.serial_device.reset_output_buffer()

  def validate_connection(self):
      try:
          self.serial_device.open()
          self.close()
          return True
      except (serial.SerialException, FileNotFoundError):
          return False

  def open(self):
      try:
          if self.is_connected():
              self.close() 

          self.serial_device.open()

          
          self.serial_device.dtr = False
          self.serial_device.rts = True
          time.sleep(0.1)
          self.serial_device.dtr = True
          self.serial_device.rts = False
          time.sleep(0.1)
          self.serial_device.dtr = False
          self.serial_device.rts = False  
          time.sleep(0.1)

          self.reset_buffer()  
          self.serial_alive = True
          

      except serial.SerialException as e:
          raise SerialError(f"Error: {e}")

  def close(self):
      if self.is_connected():
          try:
              self.serial_device.close()
              self.serial_alive = False
              
          except serial.SerialException as e:
              raise SerialError(f"Error: {e}")

  def recv(self):
      try:
          if self.serial_device.in_waiting > 0:
              bytestream = self.serial_device.read_until(DEFAULT_CRLF.encode())
              encoding = chardet.detect(bytestream)["encoding"]
              return bytestream.decode(encoding=encoding, errors="replace").strip()
          return None
      except (serial.SerialException, UnicodeDecodeError) as e:
          self.serial_alive = False
          return None

  def transmit(self, data):
      try:
          message = f"{data}\r\n"
          self.serial_device.write(message.encode())
      except serial.SerialException as e:
          print(f"⚠️ Error: {e}")

  def reconnect(self, max_attempts=5):
      attempts = 0
      while not self.serial_alive and attempts < max_attempts:
          time.sleep(3)
          try:
              self.open()
              
              return
          except SerialError:
              attempts += 1
              
      
      if not self.serial_alive:
          print("Not connected")
