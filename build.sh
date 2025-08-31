#!/bin/bash
# TinyPNG CLI 快速构建脚本
# 支持多种构建模式和平台优化

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="tinypng-cli"
VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 默认参数
BUILD_MODE="onefile"
OPTIMIZE=true
DEBUG=false
CLEAN=true
INSTALL=false
TEST_BUILD=false

# 显示帮助信息
show_help() {
    cat << EOF
🚀 TinyPNG CLI 快速构建脚本 v${VERSION}

用法: $0 [选项]

选项:
    -m, --mode MODE        构建模式: onefile (默认) 或 onedir
    -o, --no-optimize      禁用优化 (减小文件大小)
    -d, --debug            启用调试模式
    -c, --no-clean         不清理构建目录 (增量构建)
    -i, --install          构建完成后自动安装到系统
    -t, --test             构建完成后测试可执行文件
    -h, --help             显示此帮助信息

构建模式:
    onefile                创建单文件可执行文件 (推荐)
    onedir                 创建目录结构的可执行文件 (启动更快)

示例:
    $0                      # 默认构建 (onefile + 优化)
    $0 --mode onedir        # 目录模式构建
    $0 --no-optimize        # 禁用优化
    $0 --debug              # 调试模式
    $0 --install            # 构建并安装
    $0 --test               # 构建并测试

EOF
}

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${CYAN}🔨 $1${NC}"
}

# 检查依赖
check_dependencies() {
    log_info "检查构建依赖..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    # 检查 PyInstaller
    if ! python3 -c "import PyInstaller" &> /dev/null; then
        log_warning "PyInstaller 未安装，正在安装..."
        pip3 install pyinstaller
    fi
    
    log_success "依赖检查完成"
}

# 清理构建目录
clean_build_dirs() {
    if [ "$CLEAN" = true ]; then
        log_step "清理构建目录..."
        
        # 清理 dist 和 build 目录
        for dir in "dist" "build"; do
            if [ -d "$dir" ]; then
                rm -rf "$dir"
                log_info "删除目录: $dir"
            fi
        done
        
        # 清理其他构建文件
        for pattern in "*.spec" "*.egg-info"; do
            for file in $pattern; do
                if [ -e "$file" ]; then
                    rm -rf "$file"
                    log_info "删除文件: $file"
                fi
            done
        done
        
        # 清理 Python 缓存
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        
        log_success "清理完成"
    else
        log_info "跳过清理步骤"
    fi
}

# 构建可执行文件
build_executable() {
    log_step "开始构建可执行文件 (模式: $BUILD_MODE)..."
    
    # 基础 PyInstaller 命令
    cmd=(
        "python3" "-m" "PyInstaller"
        "--$BUILD_MODE"
        "--name=tinypng"
        "--distpath=./dist"
        "--workpath=./build"
        "--clean"
        "--noconfirm"
    )
    
    # 添加数据文件
    if [ -f "README.md" ]; then
        cmd+=("--add-data" "README.md:.")
    fi
    
    # 优化选项
    if [ "$OPTIMIZE" = true ]; then
        cmd+=("--strip" "--optimize=2")
    fi
    
    # 调试选项
    if [ "$DEBUG" = true ]; then
        cmd+=("--debug=all" "--log-level=DEBUG")
    fi
    
    # 平台特定优化
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if [[ "$(uname -m)" == "arm64" ]]; then
            cmd+=("--target-architecture" "universal2")
        else
            cmd+=("--target-architecture" "x86_64")
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if [ -f "linux_hook.py" ]; then
            cmd+=("--runtime-hook" "linux_hook.py")
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        if [ -f "windows_hook.py" ]; then
            cmd+=("--runtime-hook" "windows_hook.py")
        fi
    fi
    
    # 添加主脚本
    cmd+=("tinypng_cli.py")
    
    log_info "执行命令: ${cmd[*]}"
    
    if "${cmd[@]}"; then
        log_success "构建成功！"
        return 0
    else
        log_error "构建失败"
        return 1
    fi
}

# 验证可执行文件
verify_executable() {
    log_step "验证可执行文件..."
    
    executable_path="./dist/tinypng"
    
    if [ ! -f "$executable_path" ]; then
        log_error "可执行文件不存在: $executable_path"
        return 1
    fi
    
    # 检查文件大小
    size_mb=$(du -h "$executable_path" | cut -f1)
    log_info "文件大小: $size_mb"
    
    # 设置执行权限
    if [ ! -x "$executable_path" ]; then
        chmod +x "$executable_path"
        log_info "设置执行权限"
    fi
    
    # 测试运行
    log_info "测试可执行文件..."
    if timeout 10s "$executable_path" --help &> /dev/null; then
        log_success "可执行文件测试通过"
        return 0
    else
        log_warning "可执行文件测试失败"
        return 1
    fi
}

# 显示构建信息
show_build_info() {
    echo
    echo "📊 构建信息"
    echo "=================================================="
    
    executable_path="./dist/tinypng"
    if [ -f "$executable_path" ]; then
        size_mb=$(du -h "$executable_path" | cut -f1)
        build_time=$(stat -f "%Sm" "$executable_path" 2>/dev/null || stat -c "%y" "$executable_path" 2>/dev/null || echo "未知")
        
        echo "📁 输出目录: ./dist"
        echo "📦 可执行文件: $executable_path"
        echo "📏 文件大小: $size_mb"
        echo "🕒 构建时间: $build_time"
        
        # 显示系统信息
        echo "💻 操作系统: $(uname -s) $(uname -r)"
        echo "🐍 Python 版本: $(python3 --version)"
        echo "🏗️  架构: $(uname -m)"
    fi
    
    echo "=================================================="
}

# 安装到系统
install_executable() {
    if [ "$INSTALL" = true ]; then
        log_step "安装可执行文件到系统..."
        
        executable_path="./dist/tinypng"
        if [ ! -f "$executable_path" ]; then
            log_error "可执行文件不存在，无法安装"
            return 1
        fi
        
        # 安装到系统
        if sudo cp "$executable_path" /usr/local/bin/; then
            log_success "安装成功！"
            log_info "现在可以在任何地方使用 'tinypng' 命令了"
        else
            log_error "安装失败"
            return 1
        fi
    fi
}

# 测试构建结果
test_build() {
    if [ "$TEST_BUILD" = true ]; then
        log_step "测试构建结果..."
        
        executable_path="./dist/tinypng"
        if [ ! -f "$executable_path" ]; then
            log_error "可执行文件不存在，无法测试"
            return 1
        fi
        
        # 测试帮助命令
        log_info "测试帮助命令..."
        if "$executable_path" --help &> /dev/null; then
            log_success "帮助命令测试通过"
        else
            log_warning "帮助命令测试失败"
        fi
        
        # 测试版本命令
        log_info "测试版本命令..."
        if "$executable_path" --version &> /dev/null; then
            log_success "版本命令测试通过"
        else
            log_warning "版本命令测试失败"
        fi
        
        log_success "测试完成"
    fi
}

# 主构建流程
main_build() {
    log_info "🚀 开始构建 TinyPNG CLI 可执行文件..."
    log_info "构建模式: $BUILD_MODE"
    log_info "优化: $([ "$OPTIMIZE" = true ] && echo "启用" || echo "禁用")"
    log_info "调试: $([ "$DEBUG" = true ] && echo "启用" || echo "禁用")"
    
    # 检查依赖
    check_dependencies
    
    # 清理构建目录
    clean_build_dirs
    
    # 构建可执行文件
    if ! build_executable; then
        log_error "构建失败，退出"
        exit 1
    fi
    
    # 验证可执行文件
    if ! verify_executable; then
        log_warning "可执行文件验证失败，但构建可能成功"
    fi
    
    # 显示构建信息
    show_build_info
    
    # 安装到系统
    install_executable
    
    # 测试构建结果
    test_build
    
    log_success "🎉 构建流程完成！"
    
    # 显示下一步提示
    echo
    echo "💡 下一步:"
    echo "  1. 测试可执行文件: ./dist/tinypng --help"
    if [ "$INSTALL" != true ]; then
        echo "  2. 安装到系统: $0 --install"
    fi
    echo "  3. 或手动安装: sudo cp ./dist/tinypng /usr/local/bin/"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            BUILD_MODE="$2"
            shift 2
            ;;
        -o|--no-optimize)
            OPTIMIZE=false
            shift
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        -c|--no-clean)
            CLEAN=false
            shift
            ;;
        -i|--install)
            INSTALL=true
            shift
            ;;
        -t|--test)
            TEST_BUILD=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证构建模式
if [[ "$BUILD_MODE" != "onefile" && "$BUILD_MODE" != "onedir" ]]; then
    log_error "无效的构建模式: $BUILD_MODE"
    exit 1
fi

# 执行主构建流程
main_build
