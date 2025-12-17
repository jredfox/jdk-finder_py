import os
import sys
import time
import re

isWindows = True

#Use for NT Roots only Example: \\?\Harddisk0Partition3, \\?\GlobalRoot\Device\Mup\localhost\C$
def existsNTRoot(v):
    try:
        e = os.path.exists(v)
        if not e:
            os.stat(v)
        return e
    except WindowsError as we:
        if we.winerror == 5:
            return True
        return False
    except:
        pass
    return False

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

print(existsNTRoot(r'\??\Harddisk0Partition4\Recovery\WindowsRE\BLAH'))
print(os.path.exists(r'\??\Harddisk0Partition4\Recovery\WindowsRE\BLAH'))
print(normpathw(r'\??\GlobalRoot\Global??\Harddisk0Partition3'))

