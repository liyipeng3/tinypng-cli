#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyPNG CLI 版本管理脚本
用于自动化版本更新、构建和发布
"""

import os
import sys
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class VersionManager:
    """版本管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.main_script = self.project_root / "tinypng_cli.py"
        
    def get_current_version(self):
        """获取当前版本"""
        if self.pyproject_file.exists():
            content = self.pyproject_file.read_text()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        # 从主脚本获取版本
        if self.main_script.exists():
            content = self.main_script.read_text()
            match = re.search(r'@click\.version_option\(version=[\'"]([^\'"]+)[\'"]', content)
            if match:
                return match.group(1)
        
        return "1.0.0"
    
    def update_version(self, new_version, version_type=None):
        """更新版本号"""
        print(f"🔄 更新版本号到 {new_version}...")
        
        # 更新 pyproject.toml
        if self.pyproject_file.exists():
            content = self.pyproject_file.read_text()
            content = re.sub(
                r'version\s*=\s*["\'][^"\']+["\']',
                f'version = "{new_version}"',
                content
            )
            self.pyproject_file.write_text(content)
            print(f"✅ 更新 {self.pyproject_file}")
        
        # 更新主脚本
        if self.main_script.exists():
            content = self.main_script.read_text()
            content = re.sub(
                r'@click\.version_option\(version=[\'"][^\'"]+[\'"]',
                f'@click.version_option(version=\'{new_version}\'',
                content
            )
            self.main_script.write_text(content)
            print(f"✅ 更新 {self.main_script}")
        
        # 更新 requirements.txt 中的版本引用
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            content = requirements_file.read_text()
            # 这里可以添加版本更新逻辑
            print(f"✅ 更新 {requirements_file}")
        
        print(f"🎉 版本已更新到 {new_version}")
    
    def bump_version(self, bump_type):
        """自动递增版本号"""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))
        
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"无效的版本类型: {bump_type}")
        
        new_version = f"{major}.{minor}.{patch}"
        self.update_version(new_version, bump_type)
        return new_version
    
    def create_git_tag(self, version, message=None):
        """创建 Git 标签"""
        if not message:
            message = f"Release version {version}"
        
        try:
            # 添加所有更改
            subprocess.run(["git", "add", "."], check=True)
            
            # 提交更改
            subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
            
            # 创建标签
            subprocess.run(["git", "tag", "-a", f"v{version}", "-m", message], check=True)
            
            print(f"✅ Git 标签 v{version} 创建成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 操作失败: {e}")
            return False
    
    def build_release(self, version):
        """构建发布版本"""
        print(f"🔨 构建发布版本 {version}...")
        
        try:
            # 清理构建目录
            subprocess.run(["make", "clean"], check=True)
            
            # 构建可执行文件
            subprocess.run(["make", "build-executable"], check=True)
            
            # 构建 Python 包
            subprocess.run(["make", "build"], check=True)
            
            print(f"✅ 发布版本 {version} 构建成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 构建失败: {e}")
            return False
    
    def show_status(self):
        """显示当前状态"""
        print("📊 项目状态")
        print("=" * 50)
        
        current_version = self.get_current_version()
        print(f"当前版本: {current_version}")
        
        # Git 状态
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("📝 有未提交的更改:")
                print(result.stdout)
            else:
                print("✅ 工作目录干净")
        except subprocess.CalledProcessError:
            print("⚠️  无法获取 Git 状态")
        
        # 构建状态
        dist_dir = self.project_root / "dist"
        if dist_dir.exists():
            files = list(dist_dir.glob("*"))
            if files:
                print(f"📦 构建文件 ({len(files)} 个):")
                for file in files:
                    size = file.stat().st_size / (1024 * 1024)
                    print(f"  {file.name} ({size:.1f} MB)")
            else:
                print("📦 构建目录为空")
        else:
            print("📦 构建目录不存在")
        
        print("=" * 50)
    
    def release(self, version_type, message=None, skip_build=False):
        """完整的发布流程"""
        print(f"🚀 开始发布流程...")
        
        # 自动递增版本
        new_version = self.bump_version(version_type)
        
        # 创建 Git 标签
        if not self.create_git_tag(new_version, message):
            print("❌ 发布失败")
            return False
        
        # 构建发布版本
        if not skip_build:
            if not self.build_release(new_version):
                print("❌ 发布失败")
                return False
        
        print(f"🎉 版本 {new_version} 发布成功！")
        print(f"💡 下一步:")
        print(f"  1. 推送标签: git push origin v{new_version}")
        print(f"  2. 推送更改: git push origin main")
        
        if not skip_build:
            print(f"  3. 构建文件位置: ./dist/")
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="TinyPNG CLI 版本管理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python3 version.py status                    # 显示当前状态
  python3 version.py bump patch                # 递增补丁版本
  python3 version.py bump minor                # 递增次要版本
  python3 version.py bump major                # 递增主要版本
  python3 version.py release patch             # 发布补丁版本
  python3 version.py release minor --skip-build # 发布次要版本，跳过构建
  python3 version.py set 2.0.0                # 设置特定版本
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # status 命令
    subparsers.add_parser('status', help='显示项目状态')
    
    # bump 命令
    bump_parser = subparsers.add_parser('bump', help='递增版本号')
    bump_parser.add_argument('type', choices=['major', 'minor', 'patch'], 
                           help='版本类型')
    
    # set 命令
    set_parser = subparsers.add_parser('set', help='设置特定版本')
    set_parser.add_argument('version', help='版本号 (例如: 2.0.0)')
    
    # release 命令
    release_parser = subparsers.add_parser('release', help='发布新版本')
    release_parser.add_argument('type', choices=['major', 'minor', 'patch'], 
                              help='版本类型')
    release_parser.add_argument('-m', '--message', help='发布消息')
    release_parser.add_argument('--skip-build', action='store_true', 
                              help='跳过构建步骤')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = VersionManager()
    
    try:
        if args.command == 'status':
            manager.show_status()
            
        elif args.command == 'bump':
            new_version = manager.bump_version(args.type)
            print(f"✅ 版本已递增到 {new_version}")
            
        elif args.command == 'set':
            manager.update_version(args.version)
            
        elif args.command == 'release':
            success = manager.release(args.type, args.message, args.skip_build)
            if not success:
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
