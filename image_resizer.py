import os
import sys
from pathlib import Path
from PIL import Image
import argparse

class ImageResizer:
    """图片尺寸调整器"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        self.processed_count = 0
        self.error_count = 0
        self.error_files = []
    
    def is_image_file(self, file_path):
        """检查文件是否为支持的图片格式"""
        return file_path.suffix.lower() in self.supported_formats
    
    def resize_image(self, input_path, output_path, width, height, keep_aspect_ratio=True, quality=95):
        """
        调整单张图片尺寸
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            width: 目标宽度
            height: 目标高度
            keep_aspect_ratio: 是否保持宽高比
            quality: 输出质量 (1-100)
        """
        try:
            with Image.open(input_path) as img:
                # 转换为RGB模式以确保兼容性
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                
                if keep_aspect_ratio:
                    # 保持宽高比，计算实际尺寸
                    ratio = min(width / original_width, height / original_height)
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                else:
                    new_width = width
                    new_height = height
                
                # 调整尺寸
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 保存图片
                if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                    resized_img.save(output_path, 'JPEG', quality=quality, optimize=True)
                else:
                    resized_img.save(output_path, quality=quality, optimize=True)
                
                self.processed_count += 1
                return True
                
        except Exception as e:
            self.error_count += 1
            self.error_files.append((str(input_path), str(e)))
            print(f"处理图片 {input_path} 时出错: {e}")
            return False
    
    def resize_folder(self, input_folder, output_folder, width, height, 
                     keep_aspect_ratio=True, quality=95, recursive=True):
        """
        批量调整文件夹中图片尺寸
        
        Args:
            input_folder: 输入文件夹路径
            output_folder: 输出文件夹路径
            width: 目标宽度
            height: 目标高度
            keep_aspect_ratio: 是否保持宽高比
            quality: 输出质量
            recursive: 是否递归处理子文件夹
        """
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        
        if not input_path.exists():
            raise ValueError(f"输入文件夹不存在: {input_folder}")
        
        # 重置计数器
        self.processed_count = 0
        self.error_count = 0
        self.error_files = []
        
        print(f"开始处理文件夹: {input_folder}")
        print(f"目标尺寸: {width}x{height}")
        print(f"保持宽高比: {'是' if keep_aspect_ratio else '否'}")
        print(f"输出文件夹: {output_folder}")
        print("-" * 50)
        
        # 获取所有图片文件
        pattern = "**/*" if recursive else "*"
        for file_path in input_path.glob(pattern):
            if file_path.is_file() and self.is_image_file(file_path):
                # 构建输出路径，保持相对文件夹结构
                relative_path = file_path.relative_to(input_path)
                output_file_path = output_path / relative_path
                
                print(f"处理: {relative_path}")
                self.resize_image(file_path, output_file_path, width, height, 
                                keep_aspect_ratio, quality)
        
        # 输出处理结果
        print("-" * 50)
        print(f"处理完成！")
        print(f"成功处理: {self.processed_count} 张图片")
        print(f"处理失败: {self.error_count} 张图片")
        
        if self.error_files:
            print("\n处理失败的文件:")
            for file_path, error in self.error_files:
                print(f"  {file_path}: {error}")
    
    def resize_single_image(self, input_file, output_file, width, height, 
                           keep_aspect_ratio=True, quality=95):
        """调整单张图片尺寸的便捷方法"""
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        if not input_path.exists():
            raise ValueError(f"输入文件不存在: {input_file}")
        
        if not self.is_image_file(input_path):
            raise ValueError(f"不支持的图片格式: {input_file}")
        
        print(f"处理单张图片: {input_file}")
        print(f"目标尺寸: {width}x{height}")
        print(f"保持宽高比: {'是' if keep_aspect_ratio else '否'}")
        
        success = self.resize_image(input_path, output_path, width, height, 
                                  keep_aspect_ratio, quality)
        
        if success:
            print(f"处理成功，输出到: {output_file}")
        else:
            print(f"处理失败")
        
        return success


def main():
    """命令行界面"""
    parser = argparse.ArgumentParser(description='图片尺寸调整工具')
    parser.add_argument('input', help='输入文件或文件夹路径')
    parser.add_argument('output', help='输出文件或文件夹路径')
    parser.add_argument('width', type=int, help='目标宽度')
    parser.add_argument('height', type=int, help='目标高度')
    parser.add_argument('--no-aspect-ratio', action='store_true', 
                       help='不保持宽高比')
    parser.add_argument('--quality', type=int, default=95, 
                       help='输出质量 (1-100，默认95)')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归处理子文件夹')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.width <= 0 or args.height <= 0:
        print("错误: 宽度和高度必须大于0")
        sys.exit(1)
    
    if not (1 <= args.quality <= 100):
        print("错误: 质量参数必须在1-100之间")
        sys.exit(1)
    
    resizer = ImageResizer()
    input_path = Path(args.input)
    
    try:
        if input_path.is_file():
            # 处理单张图片
            resizer.resize_single_image(
                args.input, args.output, args.width, args.height,
                keep_aspect_ratio=not args.no_aspect_ratio,
                quality=args.quality
            )
        elif input_path.is_dir():
            # 处理文件夹
            resizer.resize_folder(
                args.input, args.output, args.width, args.height,
                keep_aspect_ratio=not args.no_aspect_ratio,
                quality=args.quality,
                recursive=not args.no_recursive
            )
        else:
            print(f"错误: 输入路径不存在: {args.input}")
            sys.exit(1)
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 