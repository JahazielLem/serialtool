import threading
import time
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from .serialDevice import SerialPort
from .confParser import Config


class SerialMonitor:
  def __init__(self):
    self.prompt_session = PromptSession()
    self.serial_device = SerialPort()
    self.config = Config()
    self.running_app = True
    self.cmd_char = ""
    self.data_callback = None
    self.prompt_worker = None
    self.serial_worker = None
  
  def __prompt_worker(self):
    while self.running_app:
      try:
        with patch_stdout():
          text = self.prompt_session.prompt(self.cmd_char)
          self.serial_device.transmit(text)
      except (KeyboardInterrupt, EOFError):
        self.running_app = False
        break
  
  def __rx_serial_worker(self):
    while self.running_app:
      try:
          data = self.serial_device.recv()
          if data:
            time_now = datetime.now().strftime("%H:%M:%S")
            if self.config.get_terminal_config("timestamp") != "None":
              print(f"{time_now}\t {data}")
            else:
              print(data)
            if self.data_callback:
              self.data_callback(data)
      except Exception:
        self.serial_device.close()
        self.serial_device.reconnect()

  def register_callback(self, callback):
    self.data_callback = callback  
  
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
    self.serial_device.open()
    self.cmd_char = f"[{self.serial_device.get_port()}] ?>"
    self.rx_worker()
    self.prompt()
    try:
      while self.running_app:
        time.sleep(1)
    finally:
      self.close()
      self.serial_device.close()