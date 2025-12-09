-h, --home search home and disables -h & -i if not present
-p, --path search path and disables -h & -i if not present
-i, --installs and disables -p & -i if not present
-f --full_search same as using -hip (-h -i -p)
-u update the cache a-sync seach if cache is valid and version string is <= the target
-o order of search operations 'PATH, INSTALL, HOME', 'P|I|H'
-x disables resolving javac executeable symlinks if javac symlink points from '/usr/bin/java' --> '/usr/lib/jvm/jdk-8u50/bin/javac'
-y --resolver uses java -XshowSettings:properties -version 2>&1 to determine JDK_HOME experimental. Used when javac is an actual executeable not a symlink but isn't inside a JDK Installation

jdk-finder.py -t "6-8" -u -hip -o 'INSTALL|HOME|PATH'
