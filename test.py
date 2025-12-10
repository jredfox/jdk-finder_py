import os
import sys
import glob
import time
import argparse
try:
    import ConfigParser as configparser  # Python 2
except ImportError:
    import configparser  # Python 3

#Flags
target = ''
recurse = False
quick = False
update = False
clean_cache = False
srch_all = False
search = ''
intensity = ''
paths = ''
application_bundle = ''
resolver = ''
config_load = False
flags = []

#Processed data from search application_bundle and resolver
tasks = []
bundle_JDK = True
bundle_JRE = False
rsymlinks = True
rcmd = False
custom_paths = []

#Loads the program's command line arguments into memory 
#Returns True if flags were set from the command line and the config should not load
def loadcmd():
    #Optimization for when command line args were not entered
    if len(sys.argv) < 2:
        return False
    #Define Global Vars getting edited
    global target, recurse, quick, update, clean_cache, srch_all, search, intensity, paths, application_bundle, resolver, config_load
    #Parse Command Line Args
    SENTINEL = object()
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-t','--target', metavar='"1.8."', default=SENTINEL, help='Target. Examples: "8-6", "6-8", "1.7.|1.8.|17|<9&+5 TODO: SW EW REGEX"')
    parser.add_argument('target_path', nargs='?', default=SENTINEL, metavar='"1.8."', help='Target as a Positional Paramater')
    parser.add_argument('-r','--recurse', action='store_true', default=SENTINEL, help='Deep Recursion')
    parser.add_argument('-q','--quick', action='store_true', default=SENTINEL, help='Quickly fetches the Java Path from the Cache with minimal checks')
    parser.add_argument('-u','--update', action='store_true', default=SENTINEL, help='Update Java Cache A-SYNC if the cache check succeeds and the version < max')
    parser.add_argument('-k','--clean_cache', action='store_true', default=SENTINEL, help='Cleans the Java Cache which forces a live synchronous Java search!')
    parser.add_argument('-a','--all', dest='srch_all', action='store_true', default=SENTINEL, help='Search for all Applicable Java Installs not just the first one found!')
    parser.add_argument('-s','--search', metavar='\'PATH|INSTALLS|HOME|CUSTOM\'', default=SENTINEL, help="Search Operations and Order! Example -s 'PATH|INSTALLS|HOME' Example 2: -s '*' Says to search all types and use the normal search order")
    parser.add_argument('-i','--intensity', metavar='NORMAL|MIN|OS', default=SENTINEL, help='Search Intensity where Min does minimal non extensive searches based on the search operations and OS. OS Searches Standard Official Java Installation Paths only')
    parser.add_argument('-p','--paths', metavar='\'Dir;Dir 2\'', default=SENTINEL, help='Search Custom Paths separated by \';\' or \':\' Using glob while working with -r. Replaces /bin with /Contents/Home/bin on macOs. Example: \'JDK/bin;/usr/lib/jvm/*/bin 2:~/.jdks\'. If used with -s must contain \'CUSTOM\' in the search')
    parser.add_argument('-b','--application_bundle', default=SENTINEL, metavar='JDK|JRE|ANY|*', help='Java Application Bundle Types')
    parser.add_argument('-x','--resolver', default=SENTINEL, metavar='\'SYMLINK|COMMAND|NONE\'', help="Resolve the actual path of the javac executeable! Examples: -x 'SYMLINK|COMMAND', -x '*'")
    parser.add_argument('-c','--config', dest='config_load', action='store_true', default=SENTINEL, help='Configuration Values Are Used If the CLI Has not overridden them!')
    parser.add_argument('--help', action='help', help='Show this help message and exit')

    args = parser.parse_args()
    for name, value in vars(args).items():
        if not value == SENTINEL:
            globals()[name] = value
            flags.append(name)

    #Correct Target & Flags
    if 'target_path' in flags:
        flags.remove('target_path')
    if args.target == SENTINEL and (not args.target_path == SENTINEL):
        target = args.target_path
        flags.append('target')

    return (not config_load)

def main():
    loadcmd()

    for t in tasks:
        print('task ' + t)
    print('JDK:' + str(bundle_JDK))
    print('JRE:' + str(bundle_JRE))
    print('resolve symlinks:' + str(rsymlinks))
    print('resolve cmd:' + str(rcmd))

    for p in custom_paths:
        print('path:"' + p + '"')

if __name__ == "__main__":
    main()

"""
for k, v in globals().items():
    if not k.startswith('__') and (not '<' in k) and (not '<' in str(v)):
        print(str(k) + ' "' + str(v) + '"')
"""