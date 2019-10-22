from ctypes import *

import subprocess, sys

p = subprocess.Popen("./tsl_read",shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

o, e = p.communicate()

brightness= float(o.decode('ascii'))
print("The brightness is:")
print(brightness)

