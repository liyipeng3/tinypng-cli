#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyPNG CLI 可执行文件构建脚本
支持多种构建模式和平台优化
"""

import os
import sys
import subprocess
import argparse
import platform
import shutil
from pathlib import Path

class ExecutableBuilder:
    """可执行文件构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.main_script = self.project_root / "tinypng_cli.py"
        
    def check_dependencies(self):
        """检查构建依赖"""
        print("🔍 检查构建依赖...")
        
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller 未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller 安装完成")
        
        # 检查主脚本
        if not self.main_script.exists():
            raise FileNotFoundError(f"主脚本不存在: {self.main_script}")
        
        print("✅ 依赖检查完成")
    
    def clean_build_dirs(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  删除: {dir_path}")
        
        # 清理其他构建文件
        for pattern in ["*.spec", "*.egg-info"]:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                print(f"  删除: {file_path}")
        
        print("✅ 清理完成")
    
    def build_executable(self, mode="onefile", optimize=True, debug=False):
        """构建可执行文件"""
        print(f"🔨 开始构建可执行文件 (模式: {mode})...")
        
        # 基础 PyInstaller 命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            f"--{mode}",
            "--name=tinypng",
            "--distpath", str(self.dist_dir),
            "--workpath", str(self.build_dir),
            "--clean",
            "--noconfirm"
        ]
        
        # 添加数据文件
        readme_file = self.project_root / "README.md"
        if readme_file.exists():
            cmd.extend(["--add-data", f"{readme_file}:."])
        
        # 优化选项
        if optimize:
            cmd.extend([
                "--strip",  # 去除调试符号
                "--optimize=2"  # Python 优化级别
            ])
        
        # 调试选项
        if debug:
            cmd.extend([
                "--debug=all",
                "--log-level=DEBUG"
            ])
        
        # 平台特定优化
        system = platform.system().lower()
        if system == "darwin":  # macOS
            cmd.extend([
                "--target-architecture", "universal2" if platform.machine() == "arm64" else "x86_64"
            ])
        elif system == "linux":
            cmd.extend([
                "--runtime-hook", "linux_hook.py" if (self.project_root / "linux_hook.py").exists() else ""
            ])
        elif system == "windows":
            cmd.extend([
                "--runtime-hook", "windows_hook.py" if (self.project_root / "windows_hook.py").exists() else ""
            ])
        
        # 添加主脚本
        cmd.append(str(self.main_script))
        
        # 过滤空字符串
        cmd = [arg for arg in cmd if arg]
        
        print(f"🚀 执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ 构建成功！")
            
            # 显示输出信息
            if result.stdout:
                print("📋 构建输出:")
                print(result.stdout)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 构建失败 (退出码: {e.returncode})")
            if e.stdout:
                print("📋 标准输出:")
                print(e.stdout)
            if e.stderr:
                print("❌ 错误输出:")
                print(e.stderr)
            return False
    
    def verify_executable(self):
        """验证可执行文件"""
        print("🔍 验证可执行文件...")
        
        executable_path = self.dist_dir / "tinypng"
        if not executable_path.exists():
            print("❌ 可执行文件不存在")
            return False
        
        # 检查文件大小
        size_mb = executable_path.stat().st_size / (1024 * 1024)
        print(f"📦 文件大小: {size_mb:.1f} MB")
        
        # 检查执行权限
        if not os.access(executable_path, os.X_OK):
            print("🔧 设置执行权限...")
            os.chmod(executable_path, 0o755)
        
        # 测试运行
        print("🧪 测试可执行文件...")
        try:
            result = subprocess.run([str(executable_path), "--help"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ 可执行文件测试通过")
                return True
            else:
                print(f"⚠️  可执行文件测试失败 (退出码: {result.returncode})")
                return False
        except subprocess.TimeoutExpired:
            print("⚠️  可执行文件测试超时")
            return False
        except Exception as e:
            print(f"❌ 可执行文件测试异常: {e}")
            return False
    
    def show_build_info(self):
        """显示构建信息"""
        print("\n📊 构建信息")
        print("=" * 50)
        
        executable_path = self.dist_dir / "tinypng"
        if executable_path.exists():
            stat = executable_path.stat()
            size_mb = stat.st_size / (1024 * 1024)
            
            print(f"📁 输出目录: {self.dist_dir}")
            print(f"📦 可执行文件: {executable_path}")
            print(f"📏 文件大小: {size_mb:.1f} MB")
            print(f"🕒 构建时间: {stat.st_mtime}")
            
            # 显示系统信息
            print(f"💻 操作系统: {platform.system()} {platform.release()}")
            print(f"🐍 Python 版本: {platform.python_version()}")
            print(f"🏗️  架构: {platform.machine()}")
        
        print("=" * 50)
    
    def build(self, mode="onefile", optimize=True, debug=False, clean=True):
        """完整构建流程"""
        try:
            # 检查依赖
            self.check_dependencies()
            
            # 清理构建目录
            if clean:
                self.clean_build_dirs()
            
            # 构建可执行文件
            if not self.build_executable(mode, optimize, debug):
                return False
            
            # 验证可执行文件
            if not self.verify_executable():
                return False
            
            # 显示构建信息
            self.show_build_info()
            
            print("🎉 构建流程完成！")
            return True
            
        except Exception as e:
            print(f"❌ 构建过程中发生错误: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="TinyPNG CLI 可执行文件构建脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python3 build_executable.py                    # 默认构建
  python3 build_executable.py --mode onedir      # 目录模式构建
  python3 build_executable.py --no-optimize      # 禁用优化
  python3 build_executable.py --debug            # 调试模式
  python3 build_executable.py --no-clean         # 不清理构建目录
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["onefile", "onedir"], 
        default="onefile",
        help="构建模式: onefile (单文件) 或 onedir (目录) (默认: onefile)"
    )
    
    parser.add_argument(
        "--no-optimize", 
        action="store_true",
        help="禁用优化 (减小文件大小但可能影响性能)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="启用调试模式 (增加调试信息)"
    )
    
    parser.add_argument(
        "--no-clean", 
        action="store_true",
        help="不清理构建目录 (增量构建)"
    )
    
    args = parser.parse_args()
    
    print("🚀 TinyPNG CLI 可执行文件构建器")
    print("=" * 50)
    
    builder = ExecutableBuilder()
    success = builder.build(
        mode=args.mode,
        optimize=not args.no_optimize,
        debug=args.debug,
        clean=not args.no_clean
    )
    
    if success:
        print("\n🎉 构建成功！")
        print(f"📦 可执行文件位置: {builder.dist_dir}/tinypng")
        print("\n💡 下一步:")
        print("  1. 测试可执行文件: ./dist/tinypng --help")
        print("  2. 安装到系统: make install-executable")
        print("  3. 或手动安装: sudo cp ./dist/tinypng /usr/local/bin/")
        sys.exit(0)
    else:
        print("\n❌ 构建失败！")
        print("💡 请检查错误信息并重试")
        sys.exit(1)

if __name__ == "__main__":
    main()
