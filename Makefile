# Makefile for tinypng-cli
# 支持的操作: build, clean, install, uninstall, test, format, lint, help

.PHONY: help build clean install uninstall test format lint dev-install build-executable install-executable

# 默认目标
help:
	@echo "🚀 tinypng-cli 构建系统"
	@echo "========================"
	@echo ""
	@echo "可用命令:"
	@echo "  build              - 构建 Python 包"
	@echo "  build-executable   - 构建可执行文件 (PyInstaller)"
	@echo "  clean              - 清理构建文件"
	@echo "  install            - 安装 Python 包到系统"
	@echo "  install-executable - 安装可执行文件到系统"
	@echo "  uninstall          - 卸载 Python 包"
	@echo "  test               - 运行测试"
	@echo "  format             - 格式化代码"
	@echo "  lint               - 代码检查"
	@echo "  dev-install        - 安装开发依赖"
	@echo "  help               - 显示此帮助信息"
	@echo ""

# 构建 Python 包
build:
	@echo "🔨 构建 Python 包..."
	python3 -m build
	@echo "✅ 构建完成！"

# 构建可执行文件
build-executable:
	@echo "🔨 构建可执行文件..."
	@echo "📦 安装构建依赖..."
	pip3 install pyinstaller
	@echo "🚀 使用 PyInstaller 构建..."
	python3 -m PyInstaller \
		--onefile \
		--name=tinypng \
		--distpath=./dist \
		--workpath=./build \
		--clean \
		--noconfirm \
		--add-data "README.md:." \
		tinypng_cli.py
	@echo "✅ 可执行文件构建完成！"
	@echo "📁 输出位置: ./dist/tinypng"
	@ls -lh ./dist/tinypng

# 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成！"

# 安装 Python 包到系统
install:
	@echo "📥 安装 Python 包到系统..."
	pip3 install -e .
	@echo "✅ 安装完成！"

# 安装可执行文件到系统
install-executable:
	@echo "📥 安装可执行文件到系统..."
	@if [ ! -f "./dist/tinypng" ]; then \
		echo "❌ 可执行文件不存在，请先运行 'make build-executable'"; \
		exit 1; \
	fi
	@echo "🔧 设置执行权限..."
	chmod +x ./dist/tinypng
	@echo "📦 安装到 /usr/local/bin/..."
	sudo cp ./dist/tinypng /usr/local/bin/
	@echo "✅ 安装完成！"
	@echo "🎉 现在可以在任何地方使用 'tinypng' 命令了！"

# 卸载 Python 包
uninstall:
	@echo "🗑️  卸载 Python 包..."
	pip3 uninstall tinypng-cli -y || true
	@echo "✅ 卸载完成！"

# 运行测试
test:
	@echo "🧪 运行测试..."
	python3 -m pytest tests/ -v --cov=tinypng_cli --cov-report=html
	@echo "✅ 测试完成！"

# 格式化代码
format:
	@echo "🎨 格式化代码..."
	@if command -v black >/dev/null 2>&1; then \
		black tinypng_cli.py; \
	else \
		echo "⚠️  black 未安装，跳过格式化"; \
	fi
	@echo "✅ 格式化完成！"

# 代码检查
lint:
	@echo "🔍 代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 tinypng_cli.py; \
	else \
		echo "⚠️  flake8 未安装，跳过检查"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		mypy tinypng_cli.py; \
	else \
		echo "⚠️  mypy 未安装，跳过类型检查"; \
	fi
	@echo "✅ 代码检查完成！"

# 安装开发依赖
dev-install:
	@echo "📦 安装开发依赖..."
	pip3 install -e ".[dev]"
	@echo "✅ 开发依赖安装完成！"

# 完整构建流程
all: clean build build-executable
	@echo "🎉 完整构建流程完成！"

# 开发环境设置
dev-setup: dev-install
	@echo "🔧 开发环境设置完成！"

# 发布准备
release: clean test lint build build-executable
	@echo "🚀 发布准备完成！"
	@echo "📦 可执行文件: ./dist/tinypng"
	@echo "📦 Python 包: dist/*.whl"
