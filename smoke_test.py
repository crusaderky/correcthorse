"""Test import the library and print essential information"""

import platform
import sys

import chbshash

print("Python interpreter:", sys.executable)
print("Python version    :", sys.version)
print("Platform          :", platform.platform())
print("Library path      :", chbshash.__file__)
print("Library version   :", chbshash.__version__)

assert chbshash.hash(b"hello world") == "wob demonstrations rhinoderma behaviorist"
