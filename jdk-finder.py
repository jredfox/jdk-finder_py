import os
import sys
import time
import glob
import argparse
try:
    import ConfigParser as configparser  # Python 2
except ImportError:
    import configparser  # Python 3
import re
import subprocess

###################
###################
# TODONOW:
# - recurse method may need to be optimized?????
# - cli api look into --recurse_PATH & --recurse_paths
# - make macOS work
# - make windows work
#
# TODO:
# - p make sure to replace /bin with the actual bin string
# - When JDK < Target and -u or 0 args update cache A-SYNC (-u get enabled by default inside the config when generating)
# - Add Small JDK Install search for Windows Official Oracle & Adoptium only!
# - Re-Implement jdk-finder.py V1 checks into the program so it actually works
#
# NOTES:
# -If you plan to run this program multiple times for one process please reset all the global variables back to their defaults first
# 
# Flags Done:
# * -r deep recursion instead instead of looking at specified installation locations
# * -c load the config flag values exlcuding target even if flags were entered through the command line
###################

VERSION = "2.0.0"
isWindows = os.name == 'nt'
isMac = sys.platform.lower() == 'darwin'
isLinux = not isMac and not isWindows
exe = '.exe' if isWindows else ''
VOLUME_WIN_REGEX = re.compile(
    r'(\\\\|\\)[\?\.]{1,2}\\Volume\{[0-9a-f\-]+\}\\Windows(?:\\|$)',
    re.IGNORECASE
)

dsrch = 'PATH|CUSTOM|INSTALLS'
#Flags
target = ''
recurse = False
quick = False
update = False
clean_cache = False
srch_all = False
search = dsrch
intensity = 'NORMAL'
paths = ''
application_bundle = 'JDK'
resolver = 'SYMLINK'
config_load = False
gen_override = False
flags = []

#Processed data from CLI and / or Config
tasks = []
bundle_JDK = True
bundle_JRE = False
rsymlinks = True
rcmd = False
has_resolver = True
custom_paths = []

str_bin = 'Contents/Home/bin' if isMac else 'bin'
visited = set()
javas = []
exes = ("java", "javac")

#Uses a simpler way to find JDKs using recursion.
def find_jdks_recurse():
    if isWindows:
        print('TODO:')#//TODO:
    if isMac:
        print('TODO:')#//TODO:
    else:
        findjavas('/usr/lib/jvm')
        findjavas('/usr/java')
        for p in os.listdir('/usr'):
            if p.lower().startswith('lib'):
                findjavas(os.path.join('/usr', p))
        findjavas('/etc/alternatives')
        findjavas('/opt')
        findjavas('/usr/local')
    global javas, visited
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
            if has_resolver:
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
    #Define Global Vars getting edited
    global target, recurse, quick, update, clean_cache, srch_all, search, intensity, paths, application_bundle, resolver
    #Make Config Dir
    cdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache')
    if not os.path.isdir(cdir):
        os.makedirs(cdir)
    #Generate Config Data
    cfgpath = os.path.join(cdir, 'jdkfinder.cfg')
    config = configparser.ConfigParser()
    config.add_section('main')
    sflags = ['target', 'search', 'intensity', 'paths', 'application_bundle', 'resolver']
    bflags = ['recurse', 'quick', 'update', 'clean_cache']
    if gen_override:
        for f in sflags:
            config.set('main', f, str(globals()[f]))
        for f in bflags:
            config.set('main', f, str(globals()[f]))
        config.set('main', 'all', str(srch_all))
    else:
        config.set('main', 'target', '')
        config.set('main', 'search', dsrch)
        config.set('main', 'intensity', 'NORMAL')
        config.set('main', 'paths', '')
        config.set('main', 'application_bundle', 'JDK')
        config.set('main', 'resolver', 'SYMLINK')
        for f in bflags:
            config.set('main', f, 'False')
        config.set('main', 'all', 'False')
    #Parse Config and Values into memory
    config.read(cfgpath)
    for f in sflags:
        if not f in flags:
            globals()[f] = config.get('main', f).strip()
    for f in bflags:
        if not f in flags:
            globals()[f] = config.get('main', f)[:1].lower() == 't'
    if not 'srch_all' in flags:
        srch_all = config.get('main', 'all')[:1].lower() == 't'

    #Save Config
    with open(cfgpath, 'w') as configfile:
        config.write(configfile)

#Loads the program's command line arguments into memory 
#Returns True if flags were set from the command line and the config should not load
def loadcmd():
    #Optimization for when command line args were not entered
    if len(sys.argv) < 2:
        return False
    #Define Global Vars getting edited
    global target, recurse, quick, update, clean_cache, srch_all, search, intensity, paths, application_bundle, resolver, config_load, gen_override
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
    parser.add_argument('-s','--search', metavar='\'PATH|CUSTOM|INSTALLS|HOME\'', default=SENTINEL, help="Search Operations and Order! Example -s 'CUSTOM|PATH|INSTALLS|HOME' Example 2: -s '*'. Example 3: -s 'HOME|*'")
    parser.add_argument('-i','--intensity', metavar='NORMAL|MIN|OS', default=SENTINEL, help='Search Intensity where Min does minimal non extensive searches based on the search operations and OS. OS Searches Standard Official Java Installation Paths only')
    parser.add_argument('-p','--paths', metavar='\'Dir;Dir 2\'', default=SENTINEL, help='Search Custom Paths separated by \';\' or \':\' Using glob while working with -r. Replaces /bin with /Contents/Home/bin on macOs. Example: \'JDK/bin;/usr/lib/jvm/*/bin 2:~/.jdks\'. If used with -s must contain \'CUSTOM\' in the search')
    parser.add_argument('-b','--application_bundle', default=SENTINEL, metavar='JDK|JRE|ANY|*', help='Java Application Bundle Types')
    parser.add_argument('-x','--resolver', default=SENTINEL, metavar='\'SYMLINK|COMMAND|NONE\'', help="Resolve the actual path of the javac executeable! Examples: -x 'SYMLINK|COMMAND', -x '*'")
    parser.add_argument('-c','--config', dest='config_load', action='store_true', default=SENTINEL, help='Configuration Values Are Used If the CLI Has not overridden them!')
    parser.add_argument('-g','--gen_override', action='store_true', default=SENTINEL, help='Configuration Gen Gets Overriden by Command Line Flags! Requires -c')
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

def parse():
    #Define globals to edit
    global target, search, intensity, application_bundle, resolver, tasks, bundle_JDK, bundle_JRE, rsymlinks, rcmd, has_resolver, custom_paths
    #Sanity Checks
    target = target.strip()
    search = search.replace(' ', '').upper()
    intensity = intensity.replace(' ', '').upper()
    application_bundle = application_bundle.replace(' ', '').upper()
    resolver = resolver.replace(' ', '').upper()
    if not target:
        target = '1.8.' #TODO: change to 8-6 when range support is allowed
    if not search:
        search = dsrch
    if not intensity:
        intensity = 'NORMAL'
    if not application_bundle:
        application_bundle = 'JDK'
    if not resolver:
        resolver = 'SYMLINK'

    #TODO: target parse into ranges and lists with search regex & patterns in the future instead of one static target
    
    #Parse the tasks preserving order and removing duplicates
    search = search.replace('ANY', '*').replace('*', 'PATH|CUSTOM|INSTALLS|HOME')
    ctasks = search.replace(',', '|').split('|')
    for t in ctasks:
        if not t in tasks:
            tasks.append(t)

    #Parse Application Bundle into cached booleans bundle_JDK & bundle_JRE
    if '*' in application_bundle or 'ANY' in application_bundle:
        bundle_JRE = True
        bundle_JDK = True
    else:
        bundle_JRE = 'JRE' in application_bundle or 'JAVA' in application_bundle
        bundle_JDK = 'JDK' in application_bundle
        if not bundle_JDK and not bundle_JRE:
            sys.stderr.write("Fatal Error Java Application Bundle is Invalid or Missing '" + application_bundle + "'\n")
            sys.exit(1)

    #Parse Resolver into cached useable boolean resolve_symlinks & resolve_cmd
    if '*' in resolver or 'ANY' in resolver:
        rsymlinks = True
        rcmd = True
        has_resolver = True
    else:
        rsymlinks = 'SYMLINK' in resolver or 'SYMBOLICLINK' in resolver
        rcmd = 'CMD' in resolver or 'COMMAND' in resolver
        has_resolver = rsymlinks or rcmd

    #Parse Custom Paths
    if paths:
        custom_paths = paths.strip().replace(';', ':').split(':')

if __name__ == "__main__":
    #load the default config
    if not loadcmd():
        load_cfg()
    parse()
    print(tasks)

    #Main Method Program call depending upon recurse flag
    if recurse:
        find_jdks_recurse()
    else:
        find_jdks()

    #Exit with error of 21 if not found
    sys.exit(404)