import os
import sys
import time
import glob
import argparse
try:
    import ConfigParser as configparser  # Python 2
except ImportError:
    import configparser  # Python 3

###################
###################
# TODONOW:
# - prevent config from overwriting values already found in argv
# - make macOS work
# - make windows work
#
# TODO:
# - look for solution when primary target isn't found but we prefer jdk-8
# - Add Small JDK Install search for Windows Official Oracle & Adoptium only!
# - Re-Implement jdk-finder.py V1 checks into the program so it actually works
#
# FLAGS:
# * -a Accept ALL JDKs within that match the target or all if target is "*"
# * -p PATH only search
# * -f <true/false> PATH first
# * -h Home & Local User installs like ~/.jdks
# * -m Mac Paths only. When on macOS Only Search Standard macOS JDK Installation Paths
# * -n Non Extensive search (only applies to non windows but will only check the PATH and standard installations)
# * -e extact version string match
# * -q quickly fetch it from the cache without verification other then checking if java & javac exist
# * -u update the cache a-sync after -q has ran
# * -t target may be single string, range, or an array of strings / ranges Examples: "8", "8-6", "6-8", "11-11, 17-19, 21-25+", "<6, 17+" where this matches <5 and also 17 or higher
# * -v <jre, jdk, any> accepted jdk installation types
# * -x <true/false> Resolve symlink of javac executeable itself
# * -c load the config flag values exlcuding target even if flags were entered through the command line
# 
# Flags Done:
# * -r deep recursion instead instead of looking at specified installation locations
###################

VERSION = "2.0.0"
isMac = sys.platform.lower() == 'darwin'

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

str_bin = 'Contents/Home/bin' if isMac else 'bin'
visited = set()
javas = []
exes = ("java", "javac")

#Uses a simpler way to find JDKs using recursion.
def find_jdks_recurse():
    findjavas('/usr/lib/jvm')
    findjavas('/usr/java')
    for p in os.listdir('/usr'):
        if p.lower().startswith('lib'):
            findjavas(os.path.join('/usr', p))
    findjavas('/etc/alternatives')
    findjavas('/opt')
    findjavas('/usr/local')
    global javas
    global visited
    visited = set() #clear RAM
    for jdk in javas:
        chk_jdk('found jdk:', jdk)
    javas = [] #clear RAM

def findjavas(path):
    for root, dirs, files in os.walk(path, followlinks=True):
        # Detect loop or repeated symlink target
        real = os.path.realpath(root)
        if real in visited:
            dirs[:] = []  # Don't recurse further
            continue
        visited.add(real)

        if any(t in files for t in exes):
            javas.append(real)

keys = [
    'jvm',
    'jdk',
    'java', 
    'jre',
    'adoptium',
    'termium',
    'graal',
    'corretto',
    'zulu',
    'zing',
    'semeru',
    'alibaba',
    'dragonwell',
    'bellsoft',
    'openlogic'
]
def chk_keys(name):
    name = name.lower()
    return (any(k in name for k in keys)), (name.startswith('j'))
def chk_jdk(msg, dir_path):
    print(msg + dir_path)

#Check Linx & macOS for unix like paths
def find_jdks():
    #Start Standard JDK Installation Scan
    #Handle /usr/lib/jvm/*/bin
    jvms_dir = '/usr/lib/jvm'
    if os.path.isdir(jvms_dir):
        for sub in os.listdir(jvms_dir):
            dir_jvm = os.path.join(jvms_dir, sub, str_bin)
            if(os.path.isdir(dir_jvm)):
                chk_jdk('found jdk____:', dir_jvm)

    #Handle /usr/java/*/bin (Code Duplication is 2x faster then method callings)
    jvms_dir = '/usr/java'
    if os.path.isdir(jvms_dir):
        for sub in os.listdir(jvms_dir):
            dir_jvm = os.path.join(jvms_dir, sub, str_bin)
            if(os.path.isdir(dir_jvm)):
                chk_jdk('found jdk____:', dir_jvm)

    #Handle /usr/lib*/<keyword>/bin & /usr/lib*/<keyword>/*/bin but skipping /usr/lib/jvm/*/bin
    sub_usr = os.listdir('/usr')
    for sub in sub_usr:
        if sub.lower().startswith('lib'):
            lib = os.path.join('/usr', sub)
            if os.path.isdir(lib):
                for dir_a in os.listdir(lib):
                    hasKey, hasJ = chk_keys(dir_a)
                    if hasKey or hasJ:
                        str_dir_can = os.path.join(lib, dir_a)
                        if str_dir_can == '/usr/lib/jvm':
                            continue
                        if os.path.isdir(str_dir_can):
                            str_dir_bin = os.path.join(str_dir_can, str_bin)
                            if os.path.isdir(str_dir_bin):
                                chk_jdk('found bin:', str_dir_bin)
                            if hasKey:
                                for dir_b in os.listdir(str_dir_can):
                                    str_dir_jdk = os.path.join(str_dir_can, dir_b, str_bin)
                                    if os.path.isdir(str_dir_jdk):
                                        chk_jdk('found jdk:', str_dir_jdk)
    
    #Handle /usr/lib/jvm/bin & /usr/java/bin for older javas
    old_jvm =  os.path.join('/usr/lib/jvm', str_bin)
    old_java = os.path.join('/usr/java', str_bin)
    if os.path.isdir(old_jvm):
        chk_jdk('old jvm:', old_jvm)
    if os.path.isdir(old_java):
        chk_jdk('old jvm:', old_java)

    #Handle root/<keyword> & root/<keyword>/bin & root/<keyword>/*/bin
    roots = [
        '/etc/alternatives',
        '/opt',
        '/usr/local'
    ]
    for r in roots:
        if os.path.isdir(r):
            if f_resolve_javac:
                chk_jdk('root check:', r)
            for sub in os.listdir(r):
                hasKey, hasJ = chk_keys(sub)
                if hasKey or hasJ:
                    k = os.path.join(r, sub)
                    if os.path.isdir(k):
                        k_bin = os.path.join(k, str_bin)
                        if os.path.isdir(k_bin):
                            chk_jdk('keyword_bin detected:', k_bin)
                        if hasKey:
                            for s in os.listdir(k):
                                k_jdk = os.path.join(k, s, str_bin)
                                if os.path.isdir(k_jdk):
                                    chk_jdk('sub dir:', k_jdk)

#Load the Config File
def load_cfg():
    #Make Config Dir
    cdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache')
    if not os.path.isdir(cdir):
        os.makedirs(cdir)
    #Generate Config Data
    cfgpath = os.path.join(cdir, 'jdkfinder.cfg')
    config = configparser.ConfigParser()
    config.add_section('main')
    config.set('main', 'target', '')
    config.set('main', 'r', 'false')
    config.set('main', 'q', 'false')
    config.set('main', 'u', 'false')
    config.set('main', 'p', 'false')
    config.set('main', 'f', 'true')
    config.set('main', 'h', 'false')
    config.set('main', 'm', 'false')
    config.set('main', 'n', 'false')
    config.set('main', 'e', 'false')
    config.set('main', 'a', 'false')
    config.set('main', 'v', 'JDK')
    config.set('main', 'x', 'true')
    config.set('main', 'no_path', 'false')
    #Define Global Vars getting edited
    global f_target
    global f_recurse
    global f_quick
    global f_update
    global f_path
    global f_path_first
    global f_home
    global f_mac_path
    global f_non_extensive
    global f_exact
    global f_all
    global f_value_type
    global f_resolve_javac
    global f_no_path
    #Parse Config and Values into memory
    config.read(cfgpath)
    f_target = config.get('main', 'target')
    f_recurse = config.get('main', 'r')[:1].lower() == 't'
    f_quick = config.get('main', 'q')[:1].lower() == 't'
    f_update = config.get('main', 'u')[:1].lower() == 't'
    f_path = config.get('main', 'p')[:1].lower() == 't'
    f_path_first = config.get('main', 'f')[:1].lower() == 't'
    f_home = config.get('main', 'h')[:1].lower() == 't'
    f_mac_path = config.get('main', 'm')[:1].lower() == 't'
    f_non_extensive = config.get('main', 'n')[:1].lower() == 't'
    f_exact = config.get('main', 'e')[:1].lower() == 't'
    f_all = config.get('main', 'a')[:1].lower() == 't'
    f_value_type = config.get('main', 'v')
    f_resolve_javac = config.get('main', 'x')[:1].lower() == 't'
    f_no_path = config.get('main', 'no_path')[:1].lower() == 't'
    #Save Config
    with open(cfgpath, 'w') as configfile:
        config.write(configfile)

#Loads the program's command line arguments into memory 
#Returns True if the command line has arguments
def loadcmd():
    #Optimization for when command line args were not entered
    if len(sys.argv) < 2:
        return False
    #Define Global Vars getting edited
    global f_target
    global f_recurse
    global f_quick
    global f_update
    global f_path
    global f_path_first
    global f_home
    global f_mac_path
    global f_non_extensive
    global f_exact
    global f_all
    global f_value_type
    global f_resolve_javac
    global f_config_load
    #Parse Command Line Args
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-t','--target', metavar='"1.8."', default='', help='Target')
    parser.add_argument('target_path', nargs='?', default='', metavar='"1.8."', help='Target as a Positional Paramater')
    parser.add_argument('-r','--recurse', action='store_true', help='Deep Recursion')
    parser.add_argument('-q','--quick', action='store_true', help='Quickly fetches the JDK path from the cache with minimal checks')
    parser.add_argument('-u','--update', action='store_true', help='Update Used with -q in order to update the cache a-sync if -q succeeds')
    parser.add_argument('-p','--path', action='store_true', help='PATH search only!')
    parser.add_argument('-f','--path_first', default=True, metavar='TRUE|FALSE', help='Search PATH first before looking in known JDK Installs!')
    parser.add_argument('-h','--home', action='store_true', help='Search for home & local JDK Installs by the user!')
    parser.add_argument('-m','--mac_path', action='store_true', help='Search for official macOS JDK Installs!')
    parser.add_argument('-n','--non_extensive', action='store_true', help='Search for Standard JDK Installs on the linux paths!')
    parser.add_argument('-e','--exact', action='store_true', help='JDK Version String Must Match Exactly this argument!')
    parser.add_argument('-a','--all', action='store_true', help='Search for all Applicable JDK Installs not just the first one found!')
    parser.add_argument('-v','--value_type', default='JDK', metavar='JDK|JRE|ANY', help='JDK Value Install Types')
    parser.add_argument('-x','--resolve_javac', default=True, metavar='TRUE|FALSE', help='Resolve Symbolic Links(Symlinks) of the javac executeable!')
    parser.add_argument('-c','--config_load', action='store_true', help='Config Overrides CLI flags that have not been populated yet! Normally the config only loads without any Command line(CLI) flags.')
    parser.add_argument('--no_path', action='store_true', help="Don't Search the PATH only known JDK Installs!")
    parser.add_argument('--help', action='help', help='Show this help message and exit')

    args = parser.parse_args()
    for name, value in vars(args).items():
        globals()['f_' + name] = value
    if f_target.strip() == '':
        f_target = args.target_path
    return (not f_config_load)

if __name__ == "__main__":
    #load the default config
    if not loadcmd():
        load_cfg()

    #Main Method Program call depending upon recurse flag
    if f_recurse:
        find_jdks_recurse()
    else:
        find_jdks()

    #Exit with error of 1 if not found
    sys.exit(1)