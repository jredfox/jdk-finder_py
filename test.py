import os
import sys
import glob
import time
import argparse
try:
    import ConfigParser as configparser  # Python 2
except ImportError:
    import configparser  # Python 3

isWindows = False
exe = '.exe' if isWindows else ''

str_bin = 'bin'
jdirs = set()
javas = []
exes = ("java" + exe, "javac" + exe)


#Find javas but optimized for unix (linux & macOS) Safer against symlinks
#Found from this answer https://stackoverflow.com/a/36977656
def findjavasu(d):
    for dirpath, dirnames, filenames in os.walk(d, followlinks=True):
        st = os.stat(dirpath)
        scandirs = []
        for dirname in dirnames:
            st = os.stat(os.path.join(dirpath, dirname))
            dirkey = st.st_dev, st.st_ino
            if dirkey not in jdirs:
                jdirs.add(dirkey)
                scandirs.append(dirname)
        dirnames[:] = scandirs
        if any(t in filenames for t in exes):
            javas.append(os.path.realpath(dirpath))

if __name__ == "__main__":
    findjavasu('/home/jredfox/Desktop/test')
    findjavasu('/home/jredfox/Desktop/test')
    findjavasu('/home/jredfox/Desktop/test')
    findjavasu('/home/jredfox/Desktop/test/test/test')
    print(os.path.isdir('/home/jredfox/Desktop/test/test/test/dir-link-b'))
    print(javas)
