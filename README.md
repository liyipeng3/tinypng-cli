# 🚀 TinyPNG CLI - 智能图片压缩工具

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 支持 PNG, JPEG, WebP 等格式的智能图片压缩工具，在不改变图片质量的情况下尽可能压缩体积

## ✨ 功能特性

- 🖼️ **多格式支持**: PNG, JPEG, WebP, BMP, TIFF
- 🚀 **智能压缩**: 自动选择最佳压缩算法
- 📊 **元数据保留**: 完整保留 EXIF、XMP、ICC Profile 等元数据
- 📁 **批量处理**: 支持目录批量压缩和递归处理
- 🎯 **多种预设**: fast (快速), balanced (平衡), quality (高质量)
- 📈 **实时进度**: 显示压缩进度、时间和压缩率

## 🚀 快速开始

### 安装方式

#### 方式 1: 使用可执行文件 (推荐)
```bash
# 下载对应平台的可执行文件
chmod +x tinypng
./tinypng --help
```

#### 方式 2: 从源码安装
```bash
git clone https://github.com/yourusername/tinypng-cli.git
cd tinypng-cli
pip3 install -r requirements.txt
python3 tinypng_cli.py --help
```

## 📖 使用方法

### 基本用法

```bash
# 压缩单张图片
tinypng image.png

# 指定输出文件
tinypng image.png -o compressed.png

# 指定输出格式
tinypng image.png -f jpg -o compressed.jpg

# 批量压缩目录
tinypng images/ -d compressed/

# 递归批量压缩
tinypng images/ -r -d compressed/
```

### 高级选项

```bash
# 设置 JPEG/WebP 质量
tinypng image.png -q 85

# 选择压缩预设
tinypng image.png --preset fast      # 快速压缩
tinypng image.png --preset balanced  # 平衡压缩 (默认)
tinypng image.png --preset quality   # 高质量压缩

# 覆盖已存在的文件
tinypng image.png --overwrite
```

### 批量处理示例

```bash
# 批量压缩当前目录所有图片
tinypng . -d compressed/

# 递归处理子目录
tinypng . -r -d compressed/

# 批量转换为特定格式
tinypng . -f webp -d webp_output/
```

## 🔧 构建系统

### 使用 Makefile (推荐)

```bash
# 构建可执行文件
make build-executable

# 安装到系统
make install-executable

# 查看所有可用命令
make help
```

### 使用 Shell 脚本

```bash
# 默认构建
./build.sh

# 目录模式构建 (启动更快)
./build.sh --mode onedir

# 构建并安装
./build.sh --install
```

## 🛠️ 系统要求

- **macOS**: 10.13+ (Intel/Apple Silicon)
- **Linux**: Ubuntu 18.04+, CentOS 7+
- **Windows**: Windows 10+ (需要额外配置)
- **Python**: 3.7+ (仅构建时需要)

## 🔍 故障排除

### 常见问题

```bash
# 检查文件权限
chmod +x ./dist/tinypng

# 重新构建
make clean
make build-executable
```

## 📚 相关文件

- **项目配置**: [pyproject.toml](pyproject.toml)
- **构建配置**: [pyinstaller_config.spec](pyinstaller_config.spec)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
