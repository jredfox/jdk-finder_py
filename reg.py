import os
import re
import time

VERSION_UQ = re.compile(
    r'(\d+(?:\.\d+)+(?:[\.\_\-\+\:\#\*][0-9A-Za-z]+)*)'
)
BUILD_REG = re.compile(
    r'\bbuild\b', 
    re.IGNORECASE
)

#Extract a Version String from single or double quotes. Removes any internal quotes
def getVerString(s):
    l = len(s)
    inq = False
    q = ''
    sb = ''
    i = -1
    for c in s:
        i = i + 1
        if (c == '"' or c == "'") and (not inq or q == c) and not s[i-1:i] == '\\':
            q = c if not inq else ''
            inq = not inq
        elif inq:
            sb = sb + c
        if sb and (not inq or (i+1 == l)):
            sb = sb.replace('\\"', '').replace("\\'", "").replace('\\\\', '\\').replace("'", '').replace('"', '')
            #Scans for "\d+\.\d+" at start of string
            if sb[0:1].isdigit() and '.' in sb:
               parts = sb.replace('-', '.').replace('_', '.').split('.')
               if len(parts) > 1 and parts[0].isdigit() and parts[1].isdigit():
                   return sb
            sb = ''
    return None

#Throws exception one version cannot be parsed
def get_ver(line):
    m = getVerString(line)
    if m:
        return m
    build = BUILD_REG.search(line)
    if build:
        line = line[build.start()+5:]
    return VERSION_UQ.search(line).group(1)

versions = [
    r'OpendJDK version "10000" "\"10.89.0_512-b48#Vendor:1.3.0@MYVENDOR\"" Vendor VM \"1.9.0_22\" Vendor Hotspot "1.20.0"',
    'OpenJDK version Vendor 4.0.0 \'"1.8.0_471-mix_mode"\'',
    'Java(TM) SE Runtime Environment Class Version 52.0 (build "1.8.0_471-b09")',
    'OpenJDK version \'"1.8.0_471.mix_mode"\' Vendor Version 1.8.0_471-alphawolf010',
    'OpenJDK version ( build 1.7.0_65-b48 )',
    'OpenJDK Runtime Environment Microsoft-11913448 (build 11.0.28+6-LTS)',
    'OpenJDK 64-Bit Server VM (Alibaba Dragonwell Extended Edition 8.26.25) (BUILD 25.462-b01, mixed mode)',
    'OpenJDK Runtime Environment (Alibaba Dragonwell Extended Edition 8.26.25) (build 1.8.0_462-b01)',
    r'OpendJDK version "\"\'1.0A\'\'\"" \""\"10.89.0_512-b48#Vendor:1.3.0@MY\\VENDOR\"a"\" Vendor VM \"1.9.0_22\" Vendor Hotspot "1.20.0"'
]

start = time.time()
for v in versions:
    get_ver(v)
print(time.time() - start)

