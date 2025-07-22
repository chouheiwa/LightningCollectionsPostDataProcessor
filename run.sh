#!/bin/bash

# 数据处理应用程序启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}数据处理应用程序启动脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  1  启动二进制图像反转工具 (命令行版本)"
    echo "  2  启动二进制图像反转工具 (GUI版本)"
    echo "  3  启动后数据处理工具 (命令行版本)"
    echo "  4  启动后数据处理工具 (GUI版本)"
    echo "  5  启动文件重组工具 (命令行版本)"
    echo "  6  启动文件重组工具 (GUI版本)"
    echo "  7  启动图片尺寸调整工具 (命令行版本)"
    echo "  8  启动图片尺寸调整工具 (GUI版本)"
    echo "  9  启动PNG透明像素转黑色工具 (命令行版本)"
    echo "  10 启动PNG透明像素转黑色工具 (GUI版本)"
    echo "  h  显示此帮助信息"
    echo "  q  退出"
    echo ""
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到Python3${NC}"
        echo "请安装Python3后重试"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt > /dev/null 2>&1
        echo -e "${GREEN}依赖检查完成${NC}"
    else
        echo -e "${YELLOW}未找到requirements.txt文件${NC}"
    fi
}

# 启动函数
start_binary_inverter() {
    echo -e "${GREEN}启动二进制图像反转工具 (命令行版本)...${NC}"
    python3 binary_image_inverter.py "$@"
}

start_binary_inverter_gui() {
    echo -e "${GREEN}启动二进制图像反转工具 (GUI版本)...${NC}"
    python3 binary_image_inverter_gui.py
}

start_post_process() {
    echo -e "${GREEN}启动后数据处理工具 (命令行版本)...${NC}"
    python3 post_data_process.py "$@"
}

start_post_process_gui() {
    echo -e "${GREEN}启动后数据处理工具 (GUI版本)...${NC}"
    python3 post_data_process_gui.py
}

start_file_reorganizer() {
    echo -e "${GREEN}启动文件重组工具 (命令行版本)...${NC}"
    python3 file_reorganizer.py "$@"
}

start_file_reorganizer_gui() {
    echo -e "${GREEN}启动文件重组工具 (GUI版本)...${NC}"
    python3 file_reorganizer_gui.py
}

start_image_resizer() {
    echo -e "${GREEN}启动图片尺寸调整工具 (命令行版本)...${NC}"
    python3 image_resizer.py "$@"
}

start_image_resizer_gui() {
    echo -e "${GREEN}启动图片尺寸调整工具 (GUI版本)...${NC}"
    python3 image_resizer_gui.py
}

start_transparent_to_black() {
    echo -e "${GREEN}启动PNG透明像素转黑色工具 (命令行版本)...${NC}"
    python3 transparent_to_black.py "$@"
}

start_transparent_to_black_gui() {
    echo -e "${GREEN}启动PNG透明像素转黑色工具 (GUI版本)...${NC}"
    python3 transparent_to_black_gui.py
}

# 主菜单
main_menu() {
    while true; do
        echo ""
        echo -e "${BLUE}==== 数据处理应用程序 ====${NC}"
        echo "1. 二进制图像反转工具 (命令行)"
        echo "2. 二进制图像反转工具 (GUI)"
        echo "3. 后数据处理工具 (命令行)"
        echo "4. 后数据处理工具 (GUI)"
        echo "5. 文件重组工具 (命令行)"
        echo "6. 文件重组工具 (GUI)"
        echo "7. 图片尺寸调整工具 (命令行)"
        echo "8. 图片尺寸调整工具 (GUI)"
        echo "9. PNG透明像素转黑色工具 (命令行)"
        echo "10. PNG透明像素转黑色工具 (GUI)"
        echo "h. 显示帮助"
        echo "q. 退出"
        echo ""
        read -p "请选择 (1-10/h/q): " choice
        
        case $choice in
            1)
                start_binary_inverter
                ;;
            2)
                start_binary_inverter_gui
                ;;
            3)
                start_post_process
                ;;
            4)
                start_post_process_gui
                ;;
            5)
                echo "请输入源目录路径，或按回车取消:"
                read -p "源目录: " source_dir
                if [ -n "$source_dir" ]; then
                    echo "选择合并模式:"
                    echo "1. 直接合并模式（推荐）"
                    echo "2. 保留目录结构模式"
                    read -p "请选择 (1-2): " merge_mode
                    if [ "$merge_mode" = "1" ]; then
                        start_file_reorganizer "$source_dir" --direct-merge
                    else
                        start_file_reorganizer "$source_dir"
                    fi
                fi
                ;;
            6)
                start_file_reorganizer_gui
                ;;
            7)
                echo "请输入输入路径（文件或文件夹）:"
                read -p "输入路径: " input_path
                if [ -n "$input_path" ]; then
                    echo "请输入输出路径:"
                    read -p "输出路径: " output_path
                    if [ -n "$output_path" ]; then
                        echo "请输入目标宽度:"
                        read -p "宽度: " width
                        echo "请输入目标高度:"
                        read -p "高度: " height
                        start_image_resizer "$input_path" "$output_path" "$width" "$height"
                    fi
                fi
                ;;
            8)
                start_image_resizer_gui
                ;;
            9)
                echo "请输入输入路径（PNG文件或包含PNG文件的文件夹）:"
                read -p "输入路径: " input_path
                if [ -n "$input_path" ]; then
                    echo "请输入输出路径（可选，按回车跳过）:"
                    read -p "输出路径: " output_path
                    echo "是否递归处理子文件夹？(y/n)"
                    read -p "递归处理: " recursive
                    if [ "$recursive" = "y" ] || [ "$recursive" = "Y" ]; then
                        if [ -n "$output_path" ]; then
                            start_transparent_to_black "$input_path" -o "$output_path" -r
                        else
                            start_transparent_to_black "$input_path" -r
                        fi
                    else
                        if [ -n "$output_path" ]; then
                            start_transparent_to_black "$input_path" -o "$output_path"
                        else
                            start_transparent_to_black "$input_path"
                        fi
                    fi
                fi
                ;;
            10)
                start_transparent_to_black_gui
                ;;
            h|H)
                show_help
                ;;
            q|Q)
                echo -e "${GREEN}再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选择，请重试${NC}"
                ;;
        esac
    done
}

# 主程序
main() {
    # 检查Python环境
    check_python
    
    # 如果有命令行参数，直接处理
    if [ $# -gt 0 ]; then
        case $1 in
            1)
                shift
                start_binary_inverter "$@"
                ;;
            2)
                start_binary_inverter_gui
                ;;
            3)
                shift
                start_post_process "$@"
                ;;
            4)
                start_post_process_gui
                ;;
            5)
                shift
                start_file_reorganizer "$@"
                ;;
            6)
                start_file_reorganizer_gui
                ;;
            7)
                shift
                start_image_resizer "$@"
                ;;
            8)
                start_image_resizer_gui
                ;;
            9)
                shift
                start_transparent_to_black "$@"
                ;;
            10)
                start_transparent_to_black_gui
                ;;
            -h|--help)
                show_help
                ;;
            *)
                echo -e "${RED}无效参数: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    else
        # 检查依赖
        check_dependencies
        
        # 启动交互式菜单
        main_menu
    fi
}

# 运行主程序
main "$@"