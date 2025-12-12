import os
import time
import sys

isWindows = True

if isWindows:
    if sys.version_info[0] >= 3:
        unicode = str
    from ctypes import windll, wintypes, create_unicode_buffer
    kernel32 = windll.kernel32
    INVALID_HANDLE_VALUE = -1
    FILE_READ_ATTRIBUTES = 0x80
    FILE_SHARE_ALL = 0x1 | 0x2 | 0x4  # FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
    OPEN_EXISTING = 3
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

def realpathw(path):
    path = os.path.abspath(path)  # Ensure absolute and unicode for Windows API
    if not os.path.exists(path):
        return path
    hFile = kernel32.CreateFileW(
        unicode(path),
        FILE_READ_ATTRIBUTES,
        FILE_SHARE_ALL,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    if hFile == INVALID_HANDLE_VALUE:
        return path
    try:
        sizes = [260, 32768]  # Initial, then max extended path
        for i, buf_size in enumerate(sizes):
            buffer = create_unicode_buffer(buf_size)
            ret = kernel32.GetFinalPathNameByHandleW(hFile, buffer, buf_size, 0)  # 0 = VOLUME_NAME_DOS
            if i > 0 and ret == 0:
                return path
            if ret < buf_size:
                result = buffer.value
                if i == 0:
                    colon = result.find(':')
                    if colon > 0:  # Ensure there's a char before
                        return result[(colon - 1):]
                return result
        return path
    except Exception:
        return path
    finally:
        kernel32.CloseHandle(hFile)

start = time.time()
print(os.path.realpath(r"C:\Users\jredfox\Desktop\test\infloop\infloop\..\dir-link-c"))
print(realpathw( r"C:\Users\jredfox\Desktop\test\infloop\infloop\..\dir-link-c"))
print(realpathw(r'\\?\Volume{263eee56-b1c8-408e-991a-8f0b5dae1e4b}\Users\jredfox\Desktop\test'))
print('end ' + str(time.time() - start))