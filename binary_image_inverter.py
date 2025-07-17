#!/usr/bin/env python3
"""
二值图片反转脚本
输入一张二值图片，输出反转后的图片
"""

import argparse
import os
import sys
from PIL import Image
import numpy as np


def invert_binary_image(input_path, output_path=None):
    """
    反转二值图片
    
    Args:
        input_path (str): 输入图片路径
        output_path (str): 输出图片路径，如果为None则自动生成
    
    Returns:
        str: 输出图片路径
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 读取图片
        print(f"正在读取图片: {input_path}")
        image = Image.open(input_path)
        
        # 转换为灰度图（确保是二值图）
        if image.mode != 'L':
            print(f"图片模式为 {image.mode}，正在转换为灰度图...")
            image = image.convert('L')
        
        # 转换为numpy数组进行处理
        img_array = np.array(image)
        print(f"图片尺寸: {img_array.shape}")
        
        # 检查是否为二值图（只有0和255两种值，或者接近二值）
        unique_values = np.unique(img_array)
        print(f"图片中的唯一像素值: {unique_values}")
        
        # 如果不是标准二值图，先进行二值化
        if len(unique_values) > 2:
            print("图片不是标准二值图，正在进行二值化处理...")
            # 使用127作为阈值进行二值化
            img_array = np.where(img_array > 127, 255, 0).astype(np.uint8)
            unique_values = np.unique(img_array)
            print(f"二值化后的像素值: {unique_values}")
        
        # 反转图片 (0变255，255变0)
        print("正在反转图片...")
        inverted_array = 255 - img_array
        
        # 转换回PIL图片
        inverted_image = Image.fromarray(inverted_array, mode='L')
        
        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            extension = os.path.splitext(input_path)[1]
            output_path = f"{base_name}_inverted{extension}"
        
        # 保存反转后的图片
        print(f"正在保存反转后的图片: {output_path}")
        inverted_image.save(output_path)
        
        print(f"图片反转完成！")
        print(f"输入: {input_path}")
        print(f"输出: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"处理图片时发生错误: {str(e)}")
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="二值图片反转工具")
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("-o", "--output", help="输出图片路径（可选，默认在输入文件名后加_inverted）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 设置详细输出
    if not args.verbose:
        # 如果不是详细模式，只显示关键信息
        pass
    
    # 调用图片反转函数
    result = invert_binary_image(args.input, args.output)
    
    if result:
        print(f"\n✓ 成功！反转后的图片已保存到: {result}")
        sys.exit(0)
    else:
        print("\n✗ 失败！图片反转过程中出现错误")
        sys.exit(1)


if __name__ == "__main__":
    main() 