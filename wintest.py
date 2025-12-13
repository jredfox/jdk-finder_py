import os
import time
import sys

isWindows = True

if isWindows:
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
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return path
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
        sizes = [260, 32768]
        for i, buf_size in enumerate(sizes):
            buffer = create_unicode_buffer(buf_size)
            ret = kernel32.GetFinalPathNameByHandleW(hFile, buffer, buf_size, 0)  # 0 = VOLUME_NAME_DOS
            if i > 0 and ret == 0:
                return path
            if ret < buf_size:
                result = buffer.value
                if i == 0:
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
with NoWOW64():
    print(realpathw( r"C:\Users\jredfox\Desktop\test\infloop\infloop\..\dir-link-c"))
    print(realpathw(r'\\?\Volume{263eee56-b1c8-408e-991a-8f0b5dae1e4b}\Users\jredfox\Desktop\test'))
    print(realpathw(r'C:\Program Files'))
    print(realpathw(r'C:\Windows\System32'))
    print(os.path.expandvars('%PROGRAMFILES%'))
    print(os.path.expandvars(sys.argv[1]))
    print(wintypes.HANDLE(-1).value)