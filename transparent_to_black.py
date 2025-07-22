#!/usr/bin/env python3
"""
透明像素转黑色批处理脚本
批量处理文件夹中的所有PNG图片，将透明像素转换为黑色
"""

import argparse
import os
import sys
from PIL import Image
import numpy as np
from pathlib import Path


def process_transparent_to_black(input_path, output_path=None):
    """
    将PNG图片中的透明像素转换为黑色
    
    Args:
        input_path (str): 输入图片路径
        output_path (str): 输出图片路径，如果为None则自动生成
    
    Returns:
        str: 输出图片路径，如果失败返回None
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 读取图片
        print(f"正在处理图片: {input_path}")
        image = Image.open(input_path)
        
        # 检查图片是否有透明通道
        if image.mode not in ('RGBA', 'LA', 'P'):
            print(f"图片 {os.path.basename(input_path)} 没有透明通道，跳过处理")
            return None
        
        # 转换为RGBA模式以确保有透明通道
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 转换为numpy数组
        img_array = np.array(image)
        print(f"图片尺寸: {img_array.shape}")
        
        # 检查透明像素数量
        alpha_channel = img_array[:, :, 3]
        transparent_pixels = np.sum(alpha_channel == 0)
        total_pixels = alpha_channel.size
        
        if transparent_pixels == 0:
            print(f"图片 {os.path.basename(input_path)} 没有透明像素，跳过处理")
            return None
        
        print(f"发现 {transparent_pixels} 个透明像素 (占总像素的 {transparent_pixels/total_pixels*100:.2f}%)")
        
        # 创建新的图片数组
        new_img_array = img_array.copy()
        
        # 将透明像素设置为黑色，不透明
        transparent_mask = alpha_channel == 0
        new_img_array[transparent_mask] = [0, 0, 0, 255]  # 黑色，完全不透明
        
        # 转换回PIL图片
        processed_image = Image.fromarray(new_img_array, mode='RGBA')
        
        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            extension = os.path.splitext(input_path)[1]
            output_path = f"{base_name}_no_transparent{extension}"
        
        # 保存处理后的图片
        print(f"正在保存处理后的图片: {output_path}")
        processed_image.save(output_path)
        
        print(f"图片处理完成！透明像素已转换为黑色")
        
        return output_path
        
    except Exception as e:
        print(f"处理图片时发生错误: {str(e)}")
        return None


def batch_process_folder(input_folder, output_folder=None, recursive=False):
    """
    批量处理文件夹中的所有PNG图片
    
    Args:
        input_folder (str): 输入文件夹路径
        output_folder (str): 输出文件夹路径，如果为None则在原文件名后加后缀
        recursive (bool): 是否递归处理子文件夹
    
    Returns:
        tuple: (成功处理的文件数, 跳过的文件数, 失败的文件数)
    """
    if not os.path.exists(input_folder):
        print(f"错误: 输入文件夹不存在: {input_folder}")
        return 0, 0, 1
    
    if not os.path.isdir(input_folder):
        print(f"错误: 输入路径不是文件夹: {input_folder}")
        return 0, 0, 1
    
    # 创建输出文件夹
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")
    
    # 查找所有PNG文件
    png_files = []
    if recursive:
        # 递归查找
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith('.png'):
                    png_files.append(os.path.join(root, file))
    else:
        # 只查找当前文件夹
        for file in os.listdir(input_folder):
            if file.lower().endswith('.png'):
                file_path = os.path.join(input_folder, file)
                if os.path.isfile(file_path):
                    png_files.append(file_path)
    
    if not png_files:
        print(f"在文件夹 {input_folder} 中没有找到PNG文件")
        return 0, 0, 0
    
    print(f"找到 {len(png_files)} 个PNG文件")
    print("-" * 50)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, png_file in enumerate(png_files, 1):
        print(f"\n[{i}/{len(png_files)}] 处理文件: {os.path.basename(png_file)}")
        
        # 生成输出路径
        if output_folder:
            # 保持相对路径结构
            rel_path = os.path.relpath(png_file, input_folder)
            output_path = os.path.join(output_folder, rel_path)
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        else:
            output_path = None
        
        # 处理图片
        result = process_transparent_to_black(png_file, output_path)
        
        if result:
            success_count += 1
            print(f"✓ 成功处理: {os.path.basename(result)}")
        elif result is None:
            skip_count += 1
            print(f"- 跳过文件: {os.path.basename(png_file)}")
        else:
            error_count += 1
            print(f"✗ 处理失败: {os.path.basename(png_file)}")
    
    print("\n" + "=" * 50)
    print(f"批处理完成！")
    print(f"成功处理: {success_count} 个文件")
    print(f"跳过文件: {skip_count} 个文件")
    print(f"处理失败: {error_count} 个文件")
    print(f"总计文件: {len(png_files)} 个文件")
    
    return success_count, skip_count, error_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PNG透明像素转黑色批处理工具")
    parser.add_argument("input", help="输入文件夹路径或单个PNG文件路径")
    parser.add_argument("-o", "--output", help="输出文件夹路径（可选，默认在原文件名后加_no_transparent）")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子文件夹")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    input_path = args.input
    output_path = args.output
    
    # 检查输入路径是否存在
    if not os.path.exists(input_path):
        print(f"错误: 输入路径不存在: {input_path}")
        sys.exit(1)
    
    # 判断是文件还是文件夹
    if os.path.isfile(input_path):
        # 处理单个文件
        if not input_path.lower().endswith('.png'):
            print(f"错误: 输入文件不是PNG格式: {input_path}")
            sys.exit(1)
        
        result = process_transparent_to_black(input_path, output_path)
        if result:
            print(f"\n✓ 成功！处理后的图片已保存到: {result}")
            sys.exit(0)
        else:
            print(f"\n✗ 处理失败或文件无需处理")
            sys.exit(1)
    
    elif os.path.isdir(input_path):
        # 处理文件夹
        success, skip, error = batch_process_folder(input_path, output_path, args.recursive)
        
        if error > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    
    else:
        print(f"错误: 输入路径既不是文件也不是文件夹: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()