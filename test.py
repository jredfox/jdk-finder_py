import os
import sys
import glob
import time
import argparse
try:
    import ConfigParser as configparser  # Python 2
except ImportError:
    import configparser  # Python 3

#Flag Options
f_target = ''
f_recurse = False
f_quick = False
f_update = False
f_path = False
f_path_first = True
f_home = False
f_mac_path = False
f_non_extensive = False
f_exact = False
f_all = False
f_value_type = 'JDK'
f_resolve_javac = True
f_config_load = False
f_no_path = False
flags = []

#Loads the program's command line arguments into memory 
#Returns True if flags were set from the command line and the config should not load
def loadcmd():
    #Optimization for when command line args were not entered
    if len(sys.argv) < 2:
        return False
    #Define Global Vars getting edited
    global f_target, f_recurse, f_quick, f_update, f_path, f_path_first, f_home, f_mac_path, f_non_extensive, f_exact, f_all, f_value_type, f_resolve_javac, f_config_load, f_no_path
    #Parse Command Line Args
    SENTINEL = object()
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-p','--path', action='store_true', default=SENTINEL, help='Search PATH first before looking in known JDK Installs!')

    args = parser.parse_args()
    for name, value in vars(args).items():
        if not value == SENTINEL:
            globals()['f_' + name] = value
            print(name + '=' + str(value))
            flags.append(name)

    return (not f_config_load)

loadcmd()

sys.exit(0)
for k, v in globals().items():
    if not k.startswith('__') and (not '<' in k) and (not '<' in str(v)):
        print(str(k) + ' "' + str(v) + '"')