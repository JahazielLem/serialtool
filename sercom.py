import argparse
from modules.serialDevice import DEFAULT_BAUDRATE
from modules.serialMonitor import SerialMonitor

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("port", help="Serial port")
  parser.add_argument("-b", "--baudrate", help="Baudrate", type=int, default=DEFAULT_BAUDRATE)
  args = parser.parse_args()
  
  serial_monitor = SerialMonitor()
  serial_monitor.serial_device.set_serial_port(args.port)
  serial_monitor.serial_device.set_baudrate(args.baudrate)
  try:
    serial_monitor.main()
  except Exception as e:
    raise e
  finally:
    serial_monitor.close()
