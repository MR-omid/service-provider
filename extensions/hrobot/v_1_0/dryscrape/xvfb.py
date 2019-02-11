import atexit
import os

def get_xvfb():
  from ..xvfbwrapper import  Xvfb
  if "DISPLAY" in os.environ:
    del os.environ["DISPLAY"]
  xvfb = Xvfb()
  return xvfb

