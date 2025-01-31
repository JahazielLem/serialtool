import serial
import argparse
import sys
import queue
import threading
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea, Frame

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
    
    def get_serial_port(self):
      return self.serial_device.port

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
    self.running_app = True
    self.prompt_char = 'cmd ?> '
    self.prompt_title = "Data:"

    self.prompt_worker = None
    self.__parser_args()

    # Windows style
    self.output_buffer = TextArea(style="bg:default fg:#ffffff")
    self.input_field = TextArea(height=1, prompt=self.prompt_char, multiline=False, focus_on_click=True, accept_handler=self.send_input, style="bg:default fg:#00c0de" )
    self.container = HSplit([
        Frame(self.output_buffer, title=self.prompt_title),
        self.input_field
    ])
    self.layout = Layout(self.container)
    self.bindings = self.__setup_keybindings()
    self.app = Application(layout=self.layout, key_bindings=self.bindings, full_screen=True)
  
  def __setup_keybindings(self):
    bindings = KeyBindings()

    @bindings.add("c-c")
    def _(event):
        self.runningApp = False
        event.app.exit()

    @bindings.add("c-l")
    def _(event):
        self.output_buffer.text = ""

    return bindings
  
  def __parser_args(self):
    self.parser.add_argument("port", help="Serial port")
    self.parser.add_argument("-b", "--baudrate", help="Baudrate", type=int, default=DEFAULT_BAUDRATE)
  
  def __rx_serial_worker(self):
    while self.running_app:
      data = self.serial_device.recv()
      if data:
        self.output_buffer.text += f"\n{data}"
        self.app.invalidate()
  
  def send_input(self, buffer):
    text = buffer.text.strip()
    if text:
        self.serial_device.transmit(text)
        self.app.layout.focus(self.input_field)
  
  def run_interface(self):
    self.app.layout.focus(self.input_field)
    self.app.run()
    
  def rx_worker(self):
    self.serial_worker = threading.Thread(target=self.__rx_serial_worker, daemon=True)
    self.serial_worker.start()

  def close(self):
    self.running_app = False
    if self.prompt_worker and self.prompt_worker.is_alive():
      self.prompt_worker.join(timeout=2)
    if self.serial_worker and self.serial_worker.is_alive():
      self.serial_worker.join(timeout=2)
  
  def main(self):
    args = self.parser.parse_args()
    self.serial_device.set_serial_port(args.port)
    self.serial_device.open()
    self.prompt_title = f"{self.serial_device.get_serial_port()} - {self.prompt_title}"
    self.rx_worker()
    self.run_interface()
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