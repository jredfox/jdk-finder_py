import os
import re

VERSION_CORE = r'\d+(?:\.\d+)+(?:[\.\_\-\+][0-9A-Za-z]+)*'
VERSION_Q = re.compile(
    r'[\"\'](' + VERSION_CORE + r')[\"\']'
)
VERSION_UQ = re.compile(
    r'(' + VERSION_CORE + r')'
)
BUILD_REG = re.compile(
    r'\bbuild\b', 
    re.IGNORECASE
)

#Throws exception one version cannot be parsed
def get_ver(line):
    m = VERSION_Q.search(line)
    if not m:
        build = BUILD_REG.search(line)
        if build:
            line = line[build.start()+5:]
        return VERSION_UQ.search(line).group(1)
    return m.group(1)

versions = [
    'OpenJDK version Vendor 4.0.0 \'"1.8.0_471-mix_mode"\'',
    'Java(TM) SE Runtime Environment Class Version 52.0 (build "1.8.0_471-b09")',
    'OpenJDK version \'"1.8.0_471.mix_mode"\' Vendor Version 1.8.0_471-alphawolf010',
    'OpenJDK version ( build 1.7.0_65-b48 )',
    'OpenJDK Runtime Environment Microsoft-11913448 (build 11.0.28+6-LTS)',
    'OpenJDK 64-Bit Server VM (Alibaba Dragonwell Extended Edition 8.26.25) (BUILD 25.462-b01, mixed mode)'
]

for v in versions:
    print("'" + get_ver(v) + "'")

