import argparse
import sys
from modules.serialDevice import DEFAULT_BAUDRATE
from modules.serialMonitor import SerialMonitor
from modules.confParser import Config

if __name__ == "__main__":
    config = Config()
    serial_monitor = SerialMonitor()
    parser = argparse.ArgumentParser(prog="sercom",
                                     description="Simple Serial Monitor")
    parser.add_argument("-p", "--port", help="Serial port")
    parser.add_argument(
        "-b", "--baudrate", help="Baudrate", type=int, default=DEFAULT_BAUDRATE
    )
    parser.add_argument("-ts", "--timestamp", help="Show the timestamp", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    
    serial_port = args.port
    serial_baud = args.baudrate
    if serial_port is None:
        serial_port = config.get_serial_config("port")
        serial_baud = config.get_serial_config("baudrate")
    else:
        if serial_port != config.get_serial_config(filter="port"):
            config.set_serial_config(serial_port, serial_baud)
    
    config.set_terminal_config(args.timestamp)
    
    serial_monitor.serial_device.set_serial_port(serial_port)
    serial_monitor.serial_device.set_baudrate(int(serial_baud))
    
    if not serial_monitor.serial_device.validate_connection():
        print("[Error] No serial device connection")
        sys.exit(1)
    try:
        serial_monitor.main()
    except Exception as e:
        raise e
    finally:
        serial_monitor.close()
