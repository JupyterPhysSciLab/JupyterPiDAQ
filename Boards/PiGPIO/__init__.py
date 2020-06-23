try:
    import Adafruit_ADS1x15
except (ImportError, RuntimeError, FileNotFoundError) as e:
    raise ImportError(e)

from .ADS1115 import *