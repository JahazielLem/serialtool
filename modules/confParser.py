import configparser
import os

CURRENT_DIR = os.getcwd()
CONFIG_FILENAME = "config.ini"

class Config:
  def __init__(self):
    self.config = configparser.ConfigParser()
    self.__create_config()

  def __config_path(self):
    return os.path.join(CURRENT_DIR, CONFIG_FILENAME)

  def __save_config(self):
    with open(self.__config_path(), 'w') as conf_file:
      self.config.write(conf_file)
      conf_file.close()
  
  def __read_config(self):
    self.config.read(self.__config_path())

  def __create_config(self):
    self.config["Serial"] = {
      "port": "None",
      "baudrate": "None"
    }
    self.config["Terminal"] = {
      "timestamp": True
    }
    if os.path.exists(self.__config_path()):
      self.__read_config()
    else:
      self.__save_config()
  
  def get_serial_config(self, filter=None):
    serial_config = {
      "port": self.config.get("Serial", "port"),
      "baudrate": self.config.get("Serial", "baudrate")
    }
    if filter is None:
      return serial_config
    else:
      if filter not in serial_config.keys():
        return None
      else:
        return serial_config[filter]
  
  def get_terminal_config(self, filter=None):
    terminal_config = {
      "timestamp": self.config.getboolean("Terminal", "timestamp"),
    }
    if filter is None:
      return terminal_config
    else:
      if filter not in terminal_config.keys():
        return None
      else:
        return terminal_config[filter]

  def set_serial_config(self, port, baudrate):
    self.config["Serial"] = {
      "port": port,
      "baudrate": baudrate
    }
    self.__save_config()
  
  def set_terminal_config(self, show_timestamp):
    self.config["Terminal"]["timestamp"] = str(show_timestamp)
    self.__save_config()