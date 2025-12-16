import os
import sys
import time
import re

isWindows = True

#\\?\C:\
def normpathw(v):
    #Normalize slashes
    prefix = ''
    i = -1
    p = ''
    prev = ''
    for c in v:
        i = i + 1
        if c == '/':
            c = '\\'
        if i > 1 and (prev == '\\' and c == '\\'):
            continue
        p = p + c
        prev = c
    #Correct malformed prefix of \\??\ instead of \??\
    if p.startswith('\\\\??\\'):
       p = p[1:]
    return p

print(normpathw(r'\\??\A'))
print(normpathw(r'\\\\localhost\\C$\\'))

start = time.time()
normpathw(r'C:\A\\\\My\\test///////////////////////////////////////////////////////////////////////////////path')
normpathw(r'C:\A\\\\My\\test///////////////////////////////////////////////////////////////////////////////path')
normpathw(r'C:\A\\\\My\\test///////////////////////////////////////////////////////////////////////////////path')
print(time.time() - start)

print(normpathw(r'\\\\\\\\\localhost\\\\\\\C$'))
print(os.listdir(r'\\?\Volume{300f19ef-1253-495e-90a5-2f04ac7deed0}' + "\\"))
