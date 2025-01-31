import serial
import argparse
import sys
import queue
import threading
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

DEFAULT_BAUDRATE = 115200


class SerialError(Exception):
  pass

class SerialPort:
  def __init__(self):
    self.serial_device = serial.Serial()
    self.serial_device.baudrate = DEFAULT_BAUDRATE
  
  def set_serial_port(self, port):
    self.serial_device.port = port
  
  def set_baudrate(self, baudrate):
    if baudrate not in serial.Serial.BAUDRATES:
      raise ValueError("Invalid baudrate")
    self.serial_device.baudrate = baudrate
  
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
    except serial.SerialException as e:
      print("Error: %s" % e)
      sys.exit(1)
  
  def close(self):
    if self.is_connected():
      try:
        self.serial_device.close()
      except serial.SerialException as e:
        print("Error: %s" % e)
        sys.exit(1)
  
  def recv(self):
    try:
      return self.serial_device.readline().decode().strip()
    except serial.SerialException as e:
      print(f"Error recv: {e}")
      return ""
  
  def transmit(self, data):
    message = f"{data}\r\n"
    self.serial_device.write(message.encode())
    

class SerialMonitor:
  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.prompt_session = PromptSession()
    self.serial_device = SerialPort()
    # self.rxQueue = queue.Queue()
    # self.txQueue = queue.Queue()
    self.running_app = True

    self.prompt_worker = None
    self.serial_worker = None
    self.__parser_args()
  
  def __parser_args(self):
    self.parser.add_argument("port", help="Serial port")
    self.parser.add_argument("-b", "--baudrate", help="Baudrate", type=int, default=DEFAULT_BAUDRATE)
  
  def __prompt_worker(self):
    while self.running_app:
      try:
        with patch_stdout():
          text = self.prompt_session.prompt('?> ')
          self.serial_device.transmit(text)
      except (KeyboardInterrupt, EOFError):
        self.running_app = False
        break
  
  def __rx_serial_worker(self):
    while self.running_app:
      data = self.serial_device.recv()
      print(data)
    
  def rx_worker(self):
    self.serial_worker = threading.Thread(target=self.__rx_serial_worker, daemon=True)
    self.serial_worker.start()

  def prompt(self):
    self.prompt_worker = threading.Thread(target=self.__prompt_worker, daemon=True)
    self.prompt_worker.start()

  def close(self):
    self.running_app = False
    if self.prompt_worker and self.prompt_worker.is_alive():
      self.prompt_worker.join(timeout=2)
    if self.serial_worker and self.serial_worker.is_alive():
      self.serial_worker.join(timeout=2)
      
  
  def main(self):
    args = self.parser.parse_args()
    print(args.port)
    self.serial_device.set_serial_port(args.port)
    self.serial_device.open()
    self.rx_worker()
    self.prompt()
    try:
      while self.running_app:
        time.sleep(1)
    finally:
      self.close()
      self.serial_device.close()




if __name__ == "__main__":
  monitor = SerialMonitor()
  try:
    monitor.main()
  except KeyboardInterrupt:
    print("Exiting...")
  finally:
    monitor.close()