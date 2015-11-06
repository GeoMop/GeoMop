#!/usr/bin/env python
import subprocess
import time


def main():
    print("Start - test")
    p = subprocess.Popen(["python3","job.py", "&", "disown"])
    print("Popen: " + str(p))
    time.sleep(60)
    print("End - test" )


if __name__ == '__main__':
    main()
