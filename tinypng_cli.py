#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyPNG CLI - 智能图片压缩工具
支持 PNG, JPEG, WebP 等格式的图片压缩
在不改变图片质量的情况下尽可能压缩体积
"""

import os
import sys
import click
from pathlib import Path
from PIL import Image, ImageOps
import tempfile
from tqdm import tqdm
from colorama import init, Fore, Style
import json
import piexif
import time
import threading

# 初始化 colorama (仅在支持的环境中)
try:
    init(autoreset=True)
except Exception:
    # 在不支持 colorama 的环境中继续运行
    pass

class LoadingSpinner:
    """动态 loading 图标"""
    
    def __init__(self, message="处理中"):
        self.message = message
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.running = False
        self.thread = None
    
    def start(self):
        """开始显示 loading"""
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, success=True):
        """停止 loading"""
        self.running = False
        if self.thread:
            self.thread.join()
        
        # 清除当前行，不换行
        print("\r" + " " * 100 + "\r", end="", flush=True)
        
        # 显示完成状态
        if success:
            print(f"{Fore.GREEN}✓ {self.message}完成{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {self.message}失败{Style.RESET_ALL}")
    
    def _spin(self):
        """旋转动画"""
        i = 0
        while self.running:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            print(f"\r{Fore.CYAN}{char} {self.message}...{Style.RESET_ALL}", end="", flush=True)
            time.sleep(0.1)
            i += 1

class ImageCompressor:
    """图片压缩器类"""
    
    def __init__(self, quality=85, optimize=True, progressive=True, preset='balanced'):
        self.preset = preset
        # 根据预设调整参数
        if preset == 'fast':
            self.quality = max(70, quality - 10)
            self.optimize = False
            self.progressive = False
        elif preset == 'balanced':
            self.quality = quality
            self.optimize = optimize
            self.progressive = progressive
        elif preset == 'quality':
            self.quality = min(95, quality + 5)
            self.optimize = True
            self.progressive = True
        else:
            self.quality = quality
            self.optimize = optimize
            self.progressive = progressive
        
    def _extract_metadata(self, img):
        """提取图片的元数据"""
        metadata = {}
        try:
            # 提取所有可用的元数据
            for key, value in img.info.items():
                metadata[key] = value
                    
        except Exception as e:
            print(f"{Fore.YELLOW}警告: 提取元数据失败: {e}{Style.RESET_ALL}")
            
        return metadata
    
    def _preserve_metadata(self, original_path, output_path):
        """使用 piexif 库保留 EXIF 数据"""
        try:
            # 尝试从原图提取 EXIF 数据
            with Image.open(original_path) as original_img:
                if 'exif' in original_img.info:
                    exif_data = original_img.info['exif']
                    
                    # 使用 piexif 库将 EXIF 数据写入压缩后的图片
                    try:
                        piexif.insert(exif_data, str(output_path))
                        print(f"{Fore.GREEN}✓ 成功保留 EXIF 数据{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.YELLOW}警告: EXIF 数据写入失败: {e}{Style.RESET_ALL}")
                        
        except Exception as e:
            print(f"{Fore.YELLOW}警告: 元数据处理失败: {e}{Style.RESET_ALL}")
    
    def _save_png_with_metadata(self, img, output_path, metadata):
        """保存 PNG 并保留元数据"""
        try:
            from PIL import PngImagePlugin
            
            # 创建 PNG 信息对象
            meta = PngImagePlugin.PngInfo()
            
            # 添加元数据
            for key, value in metadata.items():
                if isinstance(value, bytes):
                    # 对于二进制数据，尝试解码为文本
                    try:
                        text_value = value.decode('utf-8', errors='ignore')
                        meta.add_text(key, text_value)
                    except:
                        # 如果解码失败，跳过这个元数据
                        pass
                else:
                    meta.add_text(key, str(value))
            
            # 使用 PNG 优化保存并手动注入元数据
            img.save(output_path, 'PNG', pnginfo=meta, optimize=self.optimize, compress_level=0)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}PNG 元数据保存失败: {e}{Style.RESET_ALL}")
            return False
        
    def compress_jpeg(self, input_path, output_path):
        """压缩 JPEG 图片"""
        try:
            # 记录开始时间到实例变量
            self.start_time = time.time()
            
            # 显示压缩进度
            spinner = LoadingSpinner("压缩 JPEG 图片")
            spinner.start()
            
            with Image.open(input_path) as img:
                # 提取并保存原始元数据
                metadata = self._extract_metadata(img)
                
                # 转换为 RGB 模式（JPEG 不支持透明通道）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 准备保存参数，保留所有元数据
                save_kwargs = {
                    'quality': self.quality,
                    'optimize': self.optimize,
                    'progressive': self.progressive
                }
                
                # 将提取的元数据添加到保存参数中
                save_kwargs.update(metadata)
                
                # 保存时应用压缩设置并保留元数据
                img.save(output_path, 'JPEG', **save_kwargs)
                
                # 使用 piexif 库确保 EXIF 数据被正确保留
                self._preserve_metadata(input_path, output_path)
                
                # 先停止 loading
                spinner.stop(True)
                
                return True
        except Exception as e:
            print(f"{Fore.RED}压缩 JPEG 失败: {e}{Style.RESET_ALL}")
            return False
    
    def compress_png(self, input_path, output_path):
        """压缩 PNG 图片"""
        try:
            # 记录开始时间到实例变量
            self.start_time = time.time()
            
            # 显示压缩进度
            spinner = LoadingSpinner("压缩 PNG 图片")
            spinner.start()
            
            with Image.open(input_path) as img:
                # 提取并保存原始元数据
                metadata = self._extract_metadata(img)
                
                # 保持原始模式（支持透明通道）
                if img.mode == 'P':
                    img = img.convert('RGBA')
                
                # 使用改进的 PNG 保存方法
                success = self._save_png_with_metadata(img, output_path, metadata)
                
                if success:
                    # 先停止 loading
                    spinner.stop(success)
                else:
                    spinner.stop(success)
                
                return success
        except Exception as e:
            print(f"{Fore.RED}压缩 PNG 失败: {e}{Style.RESET_ALL}")
            return False
    
    def compress_webp(self, input_path, output_path):
        """压缩 WebP 图片"""
        try:
            # 记录开始时间到实例变量
            self.start_time = time.time()
            
            # 显示压缩进度
            spinner = LoadingSpinner("压缩 WebP 图片")
            spinner.start()
            
            with Image.open(input_path) as img:
                # 保存原始元数据
                original_info = img.info.copy()
                
                # 准备保存参数，保留所有元数据
                save_kwargs = {
                    'quality': self.quality,
                    'method': 6,  # 最高压缩方法
                    'lossless': False
                }
                
                # 保留所有重要的元数据
                for key in ['exif', 'iptc', 'xmp', 'icc_profile']:
                    if key in original_info:
                        save_kwargs[key] = original_info[key]
                
                # 转换为 RGB 模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    # 保持透明通道并保留元数据
                    img.save(output_path, 'WEBP', **save_kwargs)
                else:
                    img = img.convert('RGB')
                    img.save(output_path, 'WEBP', **save_kwargs)
                
                # 使用 piexif 库确保 EXIF 数据被正确保留
                self._preserve_metadata(input_path, output_path)
                
                # 先停止 loading
                spinner.stop(True)
                
                return True
        except Exception as e:
            print(f"{Fore.RED}压缩 WebP 失败: {e}{Style.RESET_ALL}")
            return False
    
    def compress_image(self, input_path, output_path=None, format=None, overwrite=False):
        """智能压缩图片"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"{Fore.RED}输入文件不存在: {input_path}{Style.RESET_ALL}")
            return False
        
        # 确定输出路径
        if output_path is None:
            output_path = input_path.parent / f"compressed_{input_path.name}"
        else:
            output_path = Path(output_path)
        
        # 如果输出文件已存在且不覆盖，则提示用户
        if output_path.exists() and not overwrite:
            print(f"{Fore.YELLOW}输出文件已存在: {output_path}{Style.RESET_ALL}")
            print(f"是否覆盖? (y/N): ", end="", flush=True)
            if input("").lower() != 'y':
                print(f"{Fore.YELLOW}已取消压缩{Style.RESET_ALL}")
                return False
        
        # 确定输出格式
        if format is None:
            format = input_path.suffix.lower()
        else:
            format = format.lower()
            if not format.startswith('.'):
                format = f'.{format}'
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 根据格式选择压缩方法
        success = False
        if format in ['.jpg', '.jpeg']:
            success = self.compress_jpeg(input_path, output_path)
        elif format == '.png':
            success = self.compress_png(input_path, output_path)
        elif format == '.webp':
            success = self.compress_webp(input_path, output_path)
        else:
            print(f"{Fore.YELLOW}不支持的格式: {format}，尝试自动检测...{Style.RESET_ALL}")
            # 尝试自动检测格式
            try:
                with Image.open(input_path) as img:
                    if img.format == 'JPEG':
                        success = self.compress_jpeg(input_path, output_path.with_suffix('.jpg'))
                    elif img.format == 'PNG':
                        success = self.compress_png(input_path, output_path.with_suffix('.png'))
                    elif img.format == 'WEBP':
                        success = self.compress_webp(input_path, output_path.with_suffix('.webp'))
                    else:
                        print(f"{Fore.RED}无法识别的图片格式: {img.format}{Style.RESET_ALL}")
                        return False
            except Exception as e:
                print(f"{Fore.RED}无法读取图片: {e}{Style.RESET_ALL}")
                return False
        
        if success:
            # 计算压缩率
            original_size = input_path.stat().st_size
            compressed_size = output_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100

                # 计算并显示总用时
            end_time = time.time()
            total_time = end_time - self.start_time if hasattr(self, 'start_time') else 0
            
            print(f"{Fore.GREEN}✓ 压缩成功, 总用时: {total_time:.2f}S{Style.RESET_ALL}")
            print(f"  原始大小: {self.format_size(original_size)}")
            print(f"  压缩后: {self.format_size(compressed_size)}")
            print(f"  压缩率: {compression_ratio:.1f}%")
            print(f"  输出文件: {output_path}")
                        
            return True
        else:
            print(f"{Fore.RED}✗ 压缩失败{Style.RESET_ALL}")
            return False
    
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def batch_compress(self, input_dir, output_dir=None, recursive=False, format=None, overwrite=False):
        """批量压缩图片"""
        input_dir = Path(input_dir)
        
        if not input_dir.exists() or not input_dir.is_dir():
            print(f"{Fore.RED}输入目录不存在: {input_dir}{Style.RESET_ALL}")
            return
        
        # 确定输出目录
        if output_dir is None:
            output_dir = input_dir / "compressed"
        else:
            output_dir = Path(output_dir)
        
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 支持的图片格式
        supported_formats = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        
        # 收集所有图片文件
        image_files = []
        if recursive:
            image_files = list(input_dir.rglob('*'))
        else:
            image_files = list(input_dir.glob('*'))
        
        image_files = [f for f in image_files if f.is_file() and f.suffix.lower() in supported_formats]
        
        if not image_files:
            print(f"{Fore.YELLOW}在目录 {input_dir} 中未找到支持的图片文件{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}找到 {len(image_files)} 个图片文件{Style.RESET_ALL}")
        
        # 批量压缩
        success_count = 0
        total_original_size = 0
        total_compressed_size = 0
        
        print(f"{Fore.CYAN}开始批量压缩 {len(image_files)} 张图片...{Style.RESET_ALL}")
        
        for i, image_file in enumerate(tqdm(image_files, desc="压缩进度", unit="张", ncols=80)):
            # 显示当前处理的文件
            print(f"\n{Fore.BLUE}[{i+1}/{len(image_files)}] 处理: {image_file.name}{Style.RESET_ALL}")
            
            # 计算相对路径以保持目录结构
            if recursive:
                rel_path = image_file.relative_to(input_dir)
            else:
                rel_path = image_file.name
            
            output_file = output_dir / rel_path
            
            # 确保输出文件的父目录存在
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 压缩图片
            if self.compress_image(image_file, output_file, format, overwrite):
                success_count += 1
                total_original_size += image_file.stat().st_size
                total_compressed_size += output_file.stat().st_size
        
        # 显示批量压缩结果
        print(f"\n{Fore.CYAN}批量压缩完成！{Style.RESET_ALL}")
        print(f"成功压缩: {success_count}/{len(image_files)} 张图片")
        if success_count > 0:
            total_compression_ratio = (1 - total_compressed_size / total_original_size) * 100
            print(f"总压缩率: {total_compression_ratio:.1f}%")
            print(f"节省空间: {self.format_size(total_original_size - total_compressed_size)}")

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_path', type=click.Path(), help='输出文件路径 (仅单文件模式)')
@click.option('-f', '--format', help='输出格式 (jpg, png, webp)')
@click.option('-q', '--quality', default=85, help='JPEG/WebP 质量 (1-100)', type=click.IntRange(1, 100))
@click.option('-d', '--output-dir', help='输出目录 (批量模式)')
@click.option('-r', '--recursive', is_flag=True, help='递归处理子目录 (批量模式)')
@click.option('--no-optimize', is_flag=True, help='禁用优化')
@click.option('--no-progressive', is_flag=True, help='禁用渐进式 JPEG')
@click.option('--preset', type=click.Choice(['fast', 'balanced', 'quality']), default='balanced', help='压缩预设 (fast, balanced, quality)')
@click.option('--overwrite', is_flag=True, help='覆盖已存在的输出文件')
@click.version_option(version='1.0.0', prog_name='tinypng-cli')
def main(input_path, output_path, format, quality, output_dir, recursive, no_optimize, no_progressive, preset, overwrite):
    """
    TinyPNG CLI - 智能图片压缩工具
    
    支持单文件压缩和批量压缩模式。
    
    单文件模式示例:
        tinypng-cli image.png                    # 压缩单张图片
        tinypng-cli image.png -o compressed.png  # 指定输出文件
        tinypng-cli image.png -f webp -q 90      # 转换为WebP格式，质量90
    
    批量模式示例:
        tinypng-cli images/ -d compressed/       # 批量压缩目录
        tinypng-cli images/ -r -d compressed/    # 递归批量压缩
        tinypng-cli images/ -f png               # 批量转换为PNG格式
    """
    # 参数验证和模式判断
    input_path = Path(input_path)
    
    # 判断运行模式
    is_batch_mode = input_path.is_dir()
    
    if is_batch_mode:
        # 批量模式参数验证
        if output_path:
            print(f"{Fore.YELLOW}警告: 批量模式下 -o/--output 参数将被忽略，使用 -d/--output-dir 指定输出目录{Style.RESET_ALL}")
        
        if not output_dir:
            output_dir = input_path / "compressed"
            print(f"{Fore.CYAN}未指定输出目录，使用默认目录: {output_dir}{Style.RESET_ALL}")
        
        # 批量模式
        print(f"{Fore.CYAN}开始批量压缩...{Style.RESET_ALL}")
        compressor = ImageCompressor(
            quality=quality,
            optimize=not no_optimize,
            progressive=not no_progressive,
            preset=preset
        )
        compressor.batch_compress(input_path, output_dir, recursive, format, overwrite)
        
    else:
        # 单文件模式参数验证
        if not input_path.is_file():
            print(f"{Fore.RED}错误: 输入路径必须是文件{Style.RESET_ALL}")
            sys.exit(1)
        
        if output_dir:
            print(f"{Fore.YELLOW}警告: 单文件模式下 -d/--output-dir 参数将被忽略，使用 -o/--output 指定输出文件{Style.RESET_ALL}")
        
        # 单文件压缩模式
        print(f"{Fore.CYAN}开始压缩单张图片...{Style.RESET_ALL}")
        compressor = ImageCompressor(
            quality=quality,
            optimize=not no_optimize,
            progressive=not no_progressive,
            preset=preset
        )
        success = compressor.compress_image(input_path, output_path, format, overwrite)
        if not success:
            sys.exit(1)

if __name__ == '__main__':
    main()
