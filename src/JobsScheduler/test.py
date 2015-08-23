#!/usr/bin/env python
import subprocess
import time

print( "Start - test")   
p = subprocess.Popen(["python3","job.py", "&", "disown"])
print( "Popen: " + str(p))   
time.sleep(60)
print( "End - test" )  
