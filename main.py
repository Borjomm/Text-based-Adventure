import sys

from global_state.client import Client
import globals

globals.client = Client(sys.argv)
globals.client.launch()
