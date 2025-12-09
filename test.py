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
    parser.add_argument('-t','--target', metavar='"1.8."', default=SENTINEL, help='Target. Examples: "8-6", "6-8", "1.7.|1.8.|17|<9&+5 TODO: SW EW REGEX"')
    parser.add_argument('target_path', nargs='?', default=SENTINEL, metavar='"1.8."', help='Target as a Positional Paramater')
    parser.add_argument('-r','--recurse', action='store_true', default=SENTINEL, help='Deep Recursion')
    parser.add_argument('-q','--quick', action='store_true', default=SENTINEL, help='Quickly fetches the Java Path from the Cache with minimal checks')
    parser.add_argument('-u','--update', action='store_true', default=SENTINEL, help='Update Java Cache A-SYNC if the cache check succeds and the version < max')
    parser.add_argument('-k','--clean_cache', action='store_true', default=SENTINEL, help='Cleans the Java Cache which forces a live synchronous Java search!')
    parser.add_argument('-a','--all', action='store_true', default=SENTINEL, help='Search for all Applicable Java Installs not just the first one found!')
    parser.add_argument('-s','--search', metavar='\'PATH|INSTALLS|HOME\'', default=SENTINEL, help="Search Opperations and Order! Example -s 'PATH|INSTALLS|HOME' Example 2: -s '*' Says to search all types and use the normal search order")
    parser.add_argument('-b','--application_bundle', default=SENTINEL, metavar='JDK|JRE|ANY|*', help='Java Value Install Types')
    parser.add_argument('-i','--intensity', metavar='NORMAL|MIN|OS', default=SENTINEL, help='Search Intensity where Min does minimal non extensive searches based on the search opperations and OS. OS Searches Standard Official Java Installation Paths only')
    parser.add_argument('-x','--resolver', default=SENTINEL, metavar='\'SYMLINK|COMMAND|NONE\'', help="Resolve the actual path of the javac executeable! Examples: -x 'SYMLINK|COMMAND', -x '*'")
    parser.add_argument('-c','--config_load', action='store_true', default=SENTINEL, help='Configuration Values Are Used If the CLI Has not overriden them!')
    parser.add_argument('--help', action='help', help='Show this help message and exit')

    args = parser.parse_args()
    for name, value in vars(args).items():
        if not value == SENTINEL:
            globals()['f_' + name] = value
            flags.append(name)

    #Correct Target & Flags
    if 'target_path' in flags:
        flags.remove('target_path')
    if args.target == SENTINEL and (not args.target_path == SENTINEL):
        f_target = args.target_path
        flags.append('target')
    f_path_first = str(f_path_first).lower().startswith('t')
    f_value_type = str(f_value_type)
    f_resolve_javac = str(f_resolve_javac).lower().startswith('t')

    return (not f_config_load)

loadcmd()

sys.exit(0)
for k, v in globals().items():
    if not k.startswith('__') and (not '<' in k) and (not '<' in str(v)):
        print(str(k) + ' "' + str(v) + '"')