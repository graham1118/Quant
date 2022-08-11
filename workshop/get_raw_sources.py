import time
from functions import *
import sys


i = 0
while i < int(sys.argv[1][1:]):
	print(get_10s_data())
	time.sleep(7.32)
	i += 1