import os
import sys
import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta
import argparse

# 加载Windows API
kernel32 = ctypes.windll.kernel32

# 定义Windows API函数和结构
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
OPEN_EXISTING = 3

class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD),
                ("dwHighDateTime", wintypes.DWORD)]

def set_file_time(file_path, creation_time=None, last_access_time=None, last_write_time=None):
    """
    修改文件的创建、访问和修改时间
    
    Args:
        file_path: 文件或目录路径
        creation_time: 新的创建时间 (datetime对象)
        last_access_time: 新的最后访问时间 (datetime对象)
        last_write_time: 新的最后修改时间 (datetime对象)
    """
    # 转换时间为FILETIME格式
    def to_filetime(dt):
        if dt is None:
            return None
        # 将datetime转换为Windows文件时间
        epoch = datetime(1601, 1, 1)
        ns = (dt - epoch).total_seconds() * 10**7
        ft = FILETIME()
        ft.dwHighDateTime = int(ns // (2**32))
        ft.dwLowDateTime = int(ns % (2**32))
        return ft
    
    creation_ft = to_filetime(creation_time)
    access_ft = to_filetime(last_access_time)
    write_ft = to_filetime(last_write_time)
    
    # 打开文件或目录
    handle = kernel32.CreateFileW(
        file_path,
        0x100,  # FILE_WRITE_ATTRIBUTES
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    
    if handle == -1:  # INVALID_HANDLE_VALUE
        error_code = kernel32.GetLastError()
        raise WindowsError(f"无法打开文件/目录 '{file_path}'，错误代码: {error_code}")
    
    try:
        # 设置文件时间
        if not kernel32.SetFileTime(handle,
                                   ctypes.byref(creation_ft) if creation_ft else None,
                                   ctypes.byref(access_ft) if access_ft else None,
                                   ctypes.byref(write_ft) if write_ft else None):
            error_code = kernel32.GetLastError()
            raise WindowsError(f"无法设置文件时间，错误代码: {error_code}")
        
        print(f"成功修改 '{file_path}' 的时间属性")
        
    finally:
        kernel32.CloseHandle(handle)

def parse_datetime(time_str):
    """解析日期时间字符串"""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"无法解析日期时间: {time_str}")

def main():
    parser = argparse.ArgumentParser(description="修改Windows文件/目录的创建日期")
    parser.add_argument("path", help="文件或目录路径")
    parser.add_argument("-c", "--creation", help="新的创建日期时间 (格式: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("-a", "--access", help="新的最后访问日期时间 (格式: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("-w", "--write", help="新的最后修改日期时间 (格式: YYYY-MM-DD HH:MM:SS)")
    
    args = parser.parse_args()
    
    # 检查路径是否存在
    if not os.path.exists(args.path):
        print(f"错误: 路径 '{args.path}' 不存在")
        return 1
    
    # 解析日期时间参数
    creation_time = parse_datetime(args.creation) if args.creation else None
    access_time = parse_datetime(args.access) if args.access else None
    write_time = parse_datetime(args.write) if args.write else None
    
    # 如果没有提供任何时间参数，显示当前时间
    if not any([creation_time, access_time, write_time]):
        print("错误: 请至少提供一个时间参数")
        parser.print_help()
        return 1
    
    try:
        set_file_time(args.path, creation_time, access_time, write_time)
        return 0
    except Exception as e:
        print(f"错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())