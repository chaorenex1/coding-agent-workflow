#!/bin/bash
# Orchestrator Unix/Linux/macOS 安装脚本
#
# 使用方法:
#     bash install.sh [options]
#
# 选项:
#     --skip-deps          跳过依赖检查
#     --skip-memex         跳过 memex-cli 安装
#     --skip-workflow      跳过 workflow 安装
#     --skip-requirements  跳过 requirements 安装
#     --verbose            详细输出

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "======================================================================"
echo "  Orchestrator V3 - Unix/Linux/macOS 安装程序"
echo "======================================================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到 Python 3，请先安装 Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}[信息] 找到 Python:${NC}"
python3 --version

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 运行Python安装脚本
echo ""
echo "启动 Python 安装脚本..."
echo ""

python3 "$SCRIPT_DIR/install_orchestrator.py" "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}[成功] 安装完成！${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 运行验证: python3 scripts/verify_installation.py"
    echo "  2. 运行测试: python3 orchestrator/tests/test_phase5_simple.py"
    echo "  3. 查看文档: docs/ARCHITECTURE.md"
    echo ""
else
    echo ""
    echo -e "${RED}[错误] 安装失败，请查看上述错误信息${NC}"
    exit 1
fi
