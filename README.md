# 🚀 TinyPNG CLI - 智能图片压缩工具

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/yourusername/tinypng-cli/workflows/Build%20Executables/badge.svg)](https://github.com/yourusername/tinypng-cli/actions)

> 支持 PNG, JPEG, WebP 等格式的智能图片压缩工具，在不改变图片质量的情况下尽可能压缩体积

## ✨ 功能特性

- 🖼️ **多格式支持**: PNG, JPEG, WebP, BMP, TIFF
- 🚀 **智能压缩**: 自动选择最佳压缩算法
- 📊 **元数据保留**: 完整保留 EXIF、XMP、ICC Profile 等元数据
- 📁 **批量处理**: 支持目录批量压缩和递归处理
- 🎯 **多种预设**: fast (快速), balanced (平衡), quality (高质量)
- 📈 **实时进度**: 显示压缩进度、时间和压缩率
- 🎨 **美观界面**: 彩色输出和动态 loading 图标

## 🚀 快速开始

### 安装方式

#### 方式 1: 使用可执行文件 (推荐)
```bash
# 下载对应平台的可执行文件
# 设置执行权限
chmod +x tinypng

# 测试运行
./tinypng --help
```

#### 方式 2: 从源码安装
```bash
# 克隆仓库
git clone https://github.com/yourusername/tinypng-cli.git
cd tinypng-cli

# 安装依赖
pip3 install -r requirements.txt

# 运行
python3 tinypng_cli.py --help
```

#### 方式 3: 使用构建系统
```bash
# 构建可执行文件
make build-executable

# 安装到系统
make install-executable
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

# 禁用优化
tinypng image.png --no-optimize

# 禁用渐进式 JPEG
tinypng image.png --no-progressive

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

# 设置质量和预设
tinypng . -q 90 --preset quality -d high_quality/
```

## 🔧 构建系统

### 使用 Makefile (推荐)

```bash
# 查看所有可用命令
make help

# 构建可执行文件
make build-executable

# 安装到系统
make install-executable

# 完整构建流程
make all

# 清理构建文件
make clean
```

### 使用 Shell 脚本

```bash
# 默认构建 (onefile + 优化)
./build.sh

# 目录模式构建 (启动更快)
./build.sh --mode onedir

# 构建并安装
./build.sh --install

# 构建并测试
./build.sh --test

# 调试模式
./build.sh --debug
```

### 使用 Python 脚本

```bash
# 默认构建
python3 build_executable.py

# 目录模式构建
python3 build_executable.py --mode onedir

# 调试模式
python3 build_executable.py --debug

# 增量构建
python3 build_executable.py --no-clean
```

### 版本管理

```bash
# 查看项目状态
python3 version.py status

# 递增版本号
python3 version.py bump patch    # 补丁版本
python3 version.py bump minor    # 次要版本
python3 version.py bump major    # 主要版本

# 发布新版本
python3 version.py release patch
python3 version.py release minor --skip-build
```

## 🏗️ 构建选项

### 构建模式
- **onefile**: 创建单个可执行文件 (推荐用于分发)
- **onedir**: 创建目录结构 (启动更快，适合开发)

### 优化选项
- **--strip**: 去除调试符号
- **--optimize=2**: Python 代码优化
- **--upx**: 使用 UPX 压缩 (如果可用)

### 平台特定优化
- **macOS**: 自动检测 ARM64/x86_64 架构
- **Linux**: 支持运行时钩子
- **Windows**: 支持运行时钩子

## 📦 输出文件

构建成功后，会在 `./dist/` 目录下生成：
```
./dist/
└── tinypng          # 可执行文件 (约 20MB)
```

## 🎯 最佳实践

### 开发环境
```bash
# 设置开发环境
make dev-setup

# 快速构建测试
make build-executable

# 增量构建
./build.sh --no-clean
```

### 生产环境
```bash
# 完整发布流程
make release

# 构建并安装
./build.sh --install --test

# 使用版本管理
python3 version.py release patch
```

### CI/CD 集成
```bash
# 使用 Makefile
make all

# 使用 Shell 脚本
./build.sh --mode onefile --optimize

# 使用 Python 脚本
python3 build_executable.py --mode onefile
```

## 🛠️ 系统要求

### 支持的操作系统
- ✅ **macOS**: 10.13+ (Intel/Apple Silicon)
- ✅ **Linux**: Ubuntu 18.04+, CentOS 7+
- ✅ **Windows**: Windows 10+ (需要额外配置)

### 依赖要求
- **Python**: 3.7+ (仅构建时需要)
- **内存**: 至少 2GB RAM
- **磁盘**: 至少 100MB 可用空间

## 🔍 故障排除

### 常见问题

#### 1. 可执行文件无法运行
```bash
# 检查文件权限
chmod +x ./dist/tinypng

# 检查系统兼容性
file ./dist/tinypng
```

#### 2. 权限不足
```bash
# 使用 sudo 安装
sudo make install-executable

# 或者手动安装
sudo cp ./dist/tinypng /usr/local/bin/
```

#### 3. 依赖缺失
```bash
# 重新构建
make clean
make build-executable

# 或者使用 --onedir 模式
python3 -m PyInstaller --onedir tinypng_cli.py
```

### 调试模式

```bash
# 启用详细输出
./build.sh --debug

# 查看构建日志
python3 build_executable.py --debug

# 查看帮助信息
./dist/tinypng --help
```

## 📊 性能对比

| 操作 | Python 脚本 | 可执行文件 |
|------|-------------|------------|
| **启动时间** | 1-2秒 | 0.1-0.2秒 |
| **内存占用** | 50-100MB | 20-30MB |
| **依赖管理** | 需要 Python 环境 | 完全独立 |
| **分发部署** | 复杂 | 简单 |

## 🎉 总结

通过完善的构建系统，TinyPNG CLI 现在具备了：

✅ **专业级构建系统** - 多种构建方式，满足不同需求  
✅ **自动化流程** - 从构建到发布的完整自动化  
✅ **跨平台支持** - 支持 macOS、Linux、Windows  
✅ **质量保证** - 内置测试和验证机制  
✅ **易于维护** - 清晰的文档和配置  
✅ **CI/CD 友好** - 支持自动化构建和部署  

## 📚 相关文件

- **项目配置**: [pyproject.toml](pyproject.toml)
- **构建配置**: [pyinstaller_config.spec](pyinstaller_config.spec)
- **GitHub Actions**: [.github/workflows/build.yml](.github/workflows/build.yml)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**现在你拥有了一个功能完整、性能优秀、易于维护的图片压缩工具！** 🎉
