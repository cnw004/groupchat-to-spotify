from configparser import ConfigParser

CONFIG_FILE = "configuration.ini"

class Config:
  def __init__(self):
    self.parser = ConfigParser()
    self.parser.read(CONFIG_FILE)
