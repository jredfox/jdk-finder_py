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
    parser.add_argument('-t','--target', metavar='"1.8."', default=SENTINEL, help='Target')
    parser.add_argument('target_path', nargs='?', default=SENTINEL, metavar='"1.8."', help='Target as a Positional Paramater')
    parser.add_argument('-r','--recurse', action='store_true', help='Deep Recursion')
    parser.add_argument('-q','--quick', action='store_true', help='Quickly fetches the JDK path from the cache with minimal checks')
    parser.add_argument('-u','--update', action='store_true', help='Update Used with -q in order to update the cache a-sync if -q succeeds')
    parser.add_argument('-p','--path', action='store_true', help='PATH search only!')
    parser.add_argument('-f','--path_first', default=SENTINEL, metavar='TRUE|FALSE', help='Search PATH first before looking in known JDK Installs!')
    parser.add_argument('-h','--home', action='store_true', help='Search for home & local JDK Installs by the user!')
    parser.add_argument('-m','--mac_path', action='store_true', help='Search for official macOS JDK Installs!')
    parser.add_argument('-n','--non_extensive', action='store_true', help='Search for Standard JDK Installs on the linux paths!')
    parser.add_argument('-e','--exact', action='store_true', help='JDK Version String Must Match Exactly this argument!')
    parser.add_argument('-a','--all', action='store_true', help='Search for all Applicable JDK Installs not just the first one found!')
    parser.add_argument('-v','--value_type', default=SENTINEL, metavar='JDK|JRE|ANY', help='JDK Value Install Types')
    parser.add_argument('-x','--resolve_javac', default=SENTINEL, metavar='TRUE|FALSE', help='Resolve Symbolic Links(Symlinks) of the javac executeable!')
    parser.add_argument('-c','--config_load', action='store_true', help='Config Overrides CLI flags that have not been populated yet! Normally the config only loads without any Command line(CLI) flags.')
    parser.add_argument('--no_path', action='store_true', help="Don't Search the PATH only known JDK Installs!")
    parser.add_argument('--help', action='help', help='Show this help message and exit')

    args = parser.parse_args()
    for name, value in vars(args).items():
        globals()['f_' + name] = value
        isb = isinstance(value, bool)
        if (not value == SENTINEL and not isb) or (isb and value):
            flags.append(name)

    #Correct Flags Either from being SENTINEL or not being boolean
    flags.remove('target_path')
    if f_target == SENTINEL:
        if not args.target_path == SENTINEL:
            f_target = args.target_path
            flags.append('target') 
        else:
            f_target = ''
    f_path_first = False if f_path_first == SENTINEL else str(f_path_first).lower().startswith('t')
    if f_value_type == SENTINEL:
        f_value_type = 'JDK'
    f_resolve_javac = False if f_resolve_javac == SENTINEL else str(f_resolve_javac).lower().startswith('t')

    return (not f_config_load)

loadcmd()

for k, v in globals().items():
    if not k.startswith('__') and (not '<' in k) and (not '<' in str(v)):
        print(str(k) + ' "' + str(v) + '"')