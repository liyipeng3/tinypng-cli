#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 专用构建脚本
解决 PyInstaller 在 Windows 上的兼容性问题
"""

import os
import sys
import subprocess
import shutil

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def build_windows():
    """构建 Windows 可执行文件"""
    print("开始构建 Windows 可执行文件...")
    
    # 清理之前的构建
    clean_build_dirs()
    
    # 构建命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=tinypng.exe',
        '--clean',
        '--noconfirm',
        '--distpath=./dist',
        '--workpath=./build',
        '--specpath=.',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageOps',
        '--hidden-import=PIL.PngImagePlugin',
        '--hidden-import=click',
        '--hidden-import=tqdm',
        '--hidden-import=colorama',
        '--hidden-import=piexif',
        '--hidden-import=pathlib',
        '--hidden-import=tempfile',
        '--hidden-import=threading',
        '--hidden-import=time',
        '--hidden-import=json',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        '--exclude-module=tkinter',
        '--exclude-module=PyQt5',
        '--exclude-module=PySide2',
        '--exclude-module=wx',
        'tinypng_cli.py'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        print("输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败，退出代码: {e.returncode}")
        print("错误输出:", e.stderr)
        print("标准输出:", e.stdout)
        return False

if __name__ == "__main__":
    success = build_windows()
    sys.exit(0 if success else 1)
