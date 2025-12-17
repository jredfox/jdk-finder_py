import os
import time
import sys
import re

isWindows = True

if isWindows:
    UNC_REGEX = re.compile(
        r'(\\\\|\\)[\?\.]{1,2}\\UNC' + "\\\\",
        re.IGNORECASE
    )
    VOLUME_REGEX = re.compile(
        r'(\\\\|\\)[\?\.]{1,2}\\Volume\{[0-9a-f\-]+\}(?:\\|$)',
        re.IGNORECASE
    )
    if sys.version_info[0] >= 3:
        unicode = str
    from ctypes import windll, wintypes, create_unicode_buffer, c_void_p, byref
    kernel32 = windll.kernel32
    INVALID_HANDLE_VALUE = -1
    FILE_READ_EA = 8
    FILE_READ_ATTRIBUTES = 0x80
    FILE_SHARE_ALL = 0x1 | 0x2 | 0x4  # FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
    OPEN_EXISTING = 3
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    VOLUME_NAME_GUID = 0x1
    #is32bits = sys.maxsize <= 2**32

    class NoWOW64:
        _disable = kernel32.Wow64DisableWow64FsRedirection
        _revert =  kernel32.Wow64RevertWow64FsRedirection

        def __enter__(self):
            self.old_value = c_void_p()
            self.success = self._disable(byref(self.old_value))

        def __exit__(self, type, value, traceback):
            if self.success:
                self._revert(self.old_value)
else:
    class NoWOW64:
        def __enter__(self):
            pass
        def __exit__(self, type, value, traceback):
            pass

def realpathw(path):
    FLAG_VOL_NAME = VOLUME_NAME_GUID if VOLUME_REGEX.match(path) else 0
    hFile = kernel32.CreateFileW(
        unicode(path),
        FILE_READ_EA | FILE_READ_ATTRIBUTES,
        FILE_SHARE_ALL,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    if hFile == INVALID_HANDLE_VALUE:
        return path
    try:
        sizes = [248, 32768]
        for i, buf_size in enumerate(sizes):
            buffer = create_unicode_buffer(buf_size)
            ret = kernel32.GetFinalPathNameByHandleW(hFile, buffer, buf_size, FLAG_VOL_NAME)  # 0 = VOLUME_NAME_DOS
            if ret != 0 and ret < buf_size:
                result = buffer.value
                if i == 0:
                    if UNC_REGEX.match(result):
                        iunc = result.find('UNC')
                        return '\\\\' + result[iunc+4:]
                    colon = result.find(':')
                    if colon > 0:
                        return result[(colon - 1):]
                return result
        return path
    except Exception:
        return path
    finally:
        kernel32.CloseHandle(hFile)


exe = '.exe'
jdirs = set()
javas = []
exes = ("java" + exe, "javac" + exe)

def findjavasw(d):
    for root, dirs, files in os.walk(d, followlinks=True):
        # Detect loop or repeated symlink target
        real = realpathw(root)
        if real in jdirs:
            dirs[:] = []  # Don't recurse further
            continue
        jdirs.add(real)

        if any(t in files for t in exes):
            javas.append(real)

start = time.time()

#Correct WOW64 BS given a path
def expandEnvW(p):
    if isWindows:
        l = p.lower()
        if l.startswith('@programfiles@'):
            return os.path.join(os.path.realpath('\\'), 'Program Files') + p[14:]
        elif l.startswith('@commonprogramfiles@'):
            return os.path.join(os.path.realpath('\\'), 'Program Files\\Common Files') + p[20:]
    return p

"""
Windows Operrations:
- Convert all "/" to "\" and collapse "\\" to "\". Also Removing trailing "\" but treating it as a directory if not throw error
- Fallow "." as the current dir and ".." as the parent dir according to the actual string logic not the symbolic link target
- Expand Env Variables. %VAR% / $VAR on windows and "~" as user "~/path" as relative path from the user "~<username>/" specific to a different user "$VAR" for variable
- Resolve all symlinks final path from left to right
"""

"""
My Optimzied method:
- normpathw
- Call GetFinalPathNameByHandleW if it doesn't exist start the opperation from right to left of the path until the absolute path of the resolved parrent can be found and then use that
"""
        
with NoWOW64():
    print(realpathw(r'\\?\Volume{300f19ef-1253-495e-90a5-2f04ac7deed0}' + "\\"))
    #print(realpathw(r'C:Documents'))
    #print(realpathw(r'C:\Users\jredfox\Desktop\test\dir\Desktop_B\NBTExplorer-2.8.0\..'))
    #print(realpathw(r'C:\Users\jredfox\Desktop\test\dir-link-c\Desktop_B\..\Documents'))
    #print(realpathw(r'C:\Users\jredfox\Desktop\test\dir-link-c\Desktop_B\..\Sub2'))
