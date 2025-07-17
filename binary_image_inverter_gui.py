#!/usr/bin/env python3
"""
二值图片反转GUI工具
提供图形界面来反转二值图片
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk
import numpy as np


class BinaryImageInverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("二值图片反转工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.original_image = None
        self.inverted_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入文件选择
        ttk.Label(file_frame, text="输入图片:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_input).grid(row=0, column=2)
        
        # 输出文件选择
        ttk.Label(file_frame, text="输出图片:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="浏览", command=self.browse_output).grid(row=1, column=2, pady=(10, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(0, 10))
        
        ttk.Button(button_frame, text="反转图片", command=self.invert_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清除", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="保存", command=self.save_result).pack(side=tk.LEFT)
        
        # 图片预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="图片预览", padding="10")
        preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 原图和反转后的图片显示
        ttk.Label(preview_frame, text="原图", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(0, 10))
        ttk.Label(preview_frame, text="反转后", font=("Arial", 12, "bold")).grid(row=0, column=1, pady=(0, 10))
        
        # 图片显示区域
        self.original_label = ttk.Label(preview_frame, text="请选择图片", anchor="center")
        self.original_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.inverted_label = ttk.Label(preview_frame, text="等待反转", anchor="center")
        self.inverted_label.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def browse_input(self):
        """浏览选择输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.input_path.set(file_path)
            self.load_original_image()
            # 自动生成输出路径
            base_name = os.path.splitext(file_path)[0]
            extension = os.path.splitext(file_path)[1]
            self.output_path.set(f"{base_name}_inverted{extension}")
    
    def browse_output(self):
        """浏览选择输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存反转图片",
            defaultextension=".png",
            filetypes=[
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg"),
                ("BMP文件", "*.bmp"),
                ("TIFF文件", "*.tiff"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.output_path.set(file_path)
    
    def load_original_image(self):
        """加载原图并显示"""
        try:
            input_file = self.input_path.get()
            if not os.path.exists(input_file):
                return
            
            # 加载图片
            self.original_image = Image.open(input_file)
            
            # 创建缩略图用于显示
            display_image = self.original_image.copy()
            display_image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            self.original_label.config(image=photo, text="")
            self.original_label.image = photo  # 保持引用
            
            self.status_var.set(f"已加载图片: {os.path.basename(input_file)} ({self.original_image.size[0]}x{self.original_image.size[1]})")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {str(e)}")
            self.status_var.set("加载图片失败")
    
    def invert_image(self):
        """反转图片"""
        if not self.original_image:
            messagebox.showwarning("警告", "请先选择输入图片")
            return
        
        try:
            self.status_var.set("正在反转图片...")
            self.root.update()
            
            # 转换为灰度图
            image = self.original_image.copy()
            if image.mode != 'L':
                image = image.convert('L')
            
            # 转换为numpy数组
            img_array = np.array(image)
            
            # 检查是否为二值图，如果不是则先二值化
            unique_values = np.unique(img_array)
            if len(unique_values) > 2:
                # 二值化处理
                img_array = np.where(img_array > 127, 255, 0).astype(np.uint8)
            
            # 反转图片
            inverted_array = 255 - img_array
            
            # 转换回PIL图片
            self.inverted_image = Image.fromarray(inverted_array, mode='L')
            
            # 显示反转后的图片
            display_image = self.inverted_image.copy()
            display_image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(display_image)
            self.inverted_label.config(image=photo, text="")
            self.inverted_label.image = photo  # 保持引用
            
            self.status_var.set("图片反转完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"反转图片失败: {str(e)}")
            self.status_var.set("反转失败")
    
    def save_result(self):
        """保存反转结果"""
        if not self.inverted_image:
            messagebox.showwarning("警告", "请先反转图片")
            return
        
        output_file = self.output_path.get()
        if not output_file:
            messagebox.showwarning("警告", "请指定输出文件路径")
            return
        
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 保存图片
            self.inverted_image.save(output_file)
            
            messagebox.showinfo("成功", f"反转图片已保存到:\n{output_file}")
            self.status_var.set(f"已保存: {os.path.basename(output_file)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            self.status_var.set("保存失败")
    
    def clear_all(self):
        """清除所有内容"""
        self.input_path.set("")
        self.output_path.set("")
        self.original_image = None
        self.inverted_image = None
        
        # 清除图片显示
        self.original_label.config(image="", text="请选择图片")
        self.inverted_label.config(image="", text="等待反转")
        
        # 清除引用
        self.original_label.image = None
        self.inverted_label.image = None
        
        self.status_var.set("已清除")


def main():
    """主函数"""
    root = tk.Tk()
    app = BinaryImageInverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()