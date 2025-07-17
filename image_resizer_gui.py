#!/usr/bin/env python3
"""
图片尺寸调整GUI工具
提供图形界面来批量调整图片尺寸
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from PIL import Image, ImageTk
from pathlib import Path
from image_resizer import ImageResizer


class ImageResizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片尺寸调整工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.width_var = tk.StringVar(value="800")
        self.height_var = tk.StringVar(value="600")
        self.keep_aspect_var = tk.BooleanVar(value=True)
        self.quality_var = tk.StringVar(value="95")
        self.recursive_var = tk.BooleanVar(value=True)
        self.is_folder_var = tk.BooleanVar(value=True)
        
        # 图片调整器
        self.resizer = ImageResizer()
        self.is_processing = False
        
        # 预览图片
        self.preview_image = None
        self.preview_resized = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主窗口的网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="图片尺寸调整工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 输入类型选择
        type_frame = ttk.LabelFrame(main_frame, text="输入类型", padding="10")
        type_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        type_frame.columnconfigure(0, weight=1)
        
        ttk.Radiobutton(type_frame, text="文件夹", variable=self.is_folder_var, 
                       value=True, command=self.on_type_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(type_frame, text="单张图片", variable=self.is_folder_var, 
                       value=False, command=self.on_type_change).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入路径
        ttk.Label(file_frame, text="输入:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.input_entry = ttk.Entry(file_frame, textvariable=self.input_path, width=50)
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.input_btn = ttk.Button(file_frame, text="选择文件夹", command=self.select_input)
        self.input_btn.grid(row=0, column=2)
        
        # 输出路径
        ttk.Label(file_frame, text="输出:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        self.output_btn = ttk.Button(file_frame, text="选择文件夹", command=self.select_output)
        self.output_btn.grid(row=1, column=2, pady=(5, 0))
        
        # 尺寸设置框架
        size_frame = ttk.LabelFrame(main_frame, text="尺寸设置", padding="10")
        size_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        size_frame.columnconfigure(1, weight=1)
        size_frame.columnconfigure(3, weight=1)
        
        # 宽度和高度
        ttk.Label(size_frame, text="宽度:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(size_frame, text="高度:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=0, column=3, sticky=tk.W)
        
        # 预设尺寸按钮
        preset_frame = ttk.Frame(size_frame)
        preset_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0))
        
        presets = [
            ("1920x1080", 1920, 1080),
            ("1280x720", 1280, 720),
            ("800x600", 800, 600),
            ("640x480", 640, 480),
            ("400x300", 400, 300)
        ]
        
        for i, (name, w, h) in enumerate(presets):
            btn = ttk.Button(preset_frame, text=name, 
                           command=lambda w=w, h=h: self.set_preset_size(w, h))
            btn.grid(row=0, column=i, padx=(0, 5))
        
        # 选项框架
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 保持宽高比
        ttk.Checkbutton(options_frame, text="保持宽高比", 
                       variable=self.keep_aspect_var).grid(row=0, column=0, sticky=tk.W)
        
        # 递归处理子文件夹
        self.recursive_check = ttk.Checkbutton(options_frame, text="递归处理子文件夹", 
                                             variable=self.recursive_var)
        self.recursive_check.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 质量设置
        quality_frame = ttk.Frame(options_frame)
        quality_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(quality_frame, text="输出质量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        quality_scale = ttk.Scale(quality_frame, from_=10, to=100, 
                                variable=self.quality_var, orient=tk.HORIZONTAL, length=200)
        quality_scale.grid(row=0, column=1, padx=(0, 10))
        quality_label = ttk.Label(quality_frame, textvariable=self.quality_var)
        quality_label.grid(row=0, column=2)
        
        # 预览框架
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="10")
        preview_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 原图预览
        original_frame = ttk.Frame(preview_frame)
        original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        original_frame.columnconfigure(0, weight=1)
        original_frame.rowconfigure(1, weight=1)
        
        ttk.Label(original_frame, text="原图", font=('Arial', 10, 'bold')).grid(row=0, column=0)
        self.original_canvas = tk.Canvas(original_frame, bg='white', height=200)
        self.original_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 调整后预览
        resized_frame = ttk.Frame(preview_frame)
        resized_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        resized_frame.columnconfigure(0, weight=1)
        resized_frame.rowconfigure(1, weight=1)
        
        ttk.Label(resized_frame, text="调整后", font=('Arial', 10, 'bold')).grid(row=0, column=0)
        self.resized_canvas = tk.Canvas(resized_frame, bg='white', height=200)
        self.resized_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 预览按钮
        preview_btn = ttk.Button(preview_frame, text="预览效果", command=self.preview_resize)
        preview_btn.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, pady=(10, 0))
        
        # 开始处理按钮
        self.process_btn = ttk.Button(button_frame, text="开始处理", 
                                     command=self.start_processing)
        self.process_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 停止按钮
        self.stop_btn = ttk.Button(button_frame, text="停止", 
                                  command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=8, column=0, pady=(5, 0))
        
        # 绑定事件
        width_entry.bind('<KeyRelease>', self.on_size_change)
        height_entry.bind('<KeyRelease>', self.on_size_change)
        quality_scale.bind('<Motion>', self.on_quality_change)
    
    def on_type_change(self):
        """输入类型改变时的处理"""
        if self.is_folder_var.get():
            self.input_btn.config(text="选择文件夹")
            self.output_btn.config(text="选择文件夹")
            self.recursive_check.config(state=tk.NORMAL)
        else:
            self.input_btn.config(text="选择图片")
            self.output_btn.config(text="保存为")
            self.recursive_check.config(state=tk.DISABLED)
    
    def select_input(self):
        """选择输入文件或文件夹"""
        if self.is_folder_var.get():
            path = filedialog.askdirectory(title="选择输入文件夹")
        else:
            path = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp"),
                    ("所有文件", "*.*")
                ]
            )
        
        if path:
            self.input_path.set(path)
            # 自动设置输出路径
            if self.is_folder_var.get():
                output_dir = str(Path(path).parent / f"{Path(path).name}_resized")
                self.output_path.set(output_dir)
            else:
                input_path = Path(path)
                output_file = input_path.parent / f"{input_path.stem}_resized{input_path.suffix}"
                self.output_path.set(str(output_file))
    
    def select_output(self):
        """选择输出文件或文件夹"""
        if self.is_folder_var.get():
            path = filedialog.askdirectory(title="选择输出文件夹")
        else:
            path = filedialog.asksaveasfilename(
                title="保存图片为",
                defaultextension=".jpg",
                filetypes=[
                    ("JPEG图片", "*.jpg"),
                    ("PNG图片", "*.png"),
                    ("BMP图片", "*.bmp"),
                    ("TIFF图片", "*.tiff"),
                    ("所有文件", "*.*")
                ]
            )
        
        if path:
            self.output_path.set(path)
    
    def set_preset_size(self, width, height):
        """设置预设尺寸"""
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        self.on_size_change()
    
    def on_size_change(self, event=None):
        """尺寸改变时更新预览"""
        if hasattr(self, 'preview_image') and self.preview_image:
            self.update_preview()
    
    def on_quality_change(self, event=None):
        """质量滑块改变时的处理"""
        # 更新质量显示为整数
        quality = int(float(self.quality_var.get()))
        self.quality_var.set(str(quality))
    
    def preview_resize(self):
        """预览调整效果"""
        if not self.input_path.get():
            messagebox.showwarning("警告", "请先选择输入路径")
            return
        
        try:
            if self.is_folder_var.get():
                # 文件夹模式：选择第一张图片进行预览
                input_folder = Path(self.input_path.get())
                image_files = []
                for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']:
                    image_files.extend(input_folder.glob(f"*{ext}"))
                    image_files.extend(input_folder.glob(f"*{ext.upper()}"))
                
                if not image_files:
                    messagebox.showinfo("信息", "文件夹中没有找到图片文件")
                    return
                
                preview_file = image_files[0]
            else:
                # 单文件模式
                preview_file = Path(self.input_path.get())
            
            # 加载原图
            self.preview_image = Image.open(preview_file)
            self.show_original_preview()
            
            # 生成调整后的预览
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {e}")
    
    def show_original_preview(self):
        """显示原图预览"""
        if not self.preview_image:
            return
        
        # 计算适合canvas的尺寸
        canvas_width = self.original_canvas.winfo_width()
        canvas_height = self.original_canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas还没有渲染
            self.root.after(100, self.show_original_preview)
            return
        
        # 计算缩放比例
        img_width, img_height = self.preview_image.size
        scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # 调整图片大小并显示
        display_img = self.preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.original_photo = ImageTk.PhotoImage(display_img)
        
        self.original_canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.original_canvas.create_image(x, y, anchor=tk.NW, image=self.original_photo)
    
    def update_preview(self):
        """更新调整后的预览"""
        if not self.preview_image:
            return
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width <= 0 or height <= 0:
                return
            
            # 计算实际尺寸
            if self.keep_aspect_var.get():
                original_width, original_height = self.preview_image.size
                ratio = min(width / original_width, height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            else:
                new_width = width
                new_height = height
            
            # 生成调整后的图片
            self.preview_resized = self.preview_image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS)
            
            self.show_resized_preview()
            
        except ValueError:
            pass  # 输入无效时忽略
    
    def show_resized_preview(self):
        """显示调整后的预览"""
        if not self.preview_resized:
            return
        
        # 计算适合canvas的尺寸
        canvas_width = self.resized_canvas.winfo_width()
        canvas_height = self.resized_canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas还没有渲染
            self.root.after(100, self.show_resized_preview)
            return
        
        # 计算缩放比例
        img_width, img_height = self.preview_resized.size
        scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)
        
        if scale < 1.0:
            display_width = int(img_width * scale)
            display_height = int(img_height * scale)
            display_img = self.preview_resized.resize(
                (display_width, display_height), Image.Resampling.LANCZOS)
        else:
            display_img = self.preview_resized
            display_width, display_height = img_width, img_height
        
        # 显示图片
        self.resized_photo = ImageTk.PhotoImage(display_img)
        
        self.resized_canvas.delete("all")
        x = (canvas_width - display_width) // 2
        y = (canvas_height - display_height) // 2
        self.resized_canvas.create_image(x, y, anchor=tk.NW, image=self.resized_photo)
    
    def validate_inputs(self):
        """验证输入参数"""
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入路径")
            return False
        
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出路径")
            return False
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if width <= 0 or height <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "请输入有效的宽度和高度")
            return False
        
        try:
            quality = int(float(self.quality_var.get()))
            if not (1 <= quality <= 100):
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "质量参数必须在1-100之间")
            return False
        
        return True
    
    def start_processing(self):
        """开始处理"""
        if not self.validate_inputs():
            return
        
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return
        
        # 启动处理线程
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.status_label.config(text="正在处理...")
        
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()
    
    def process_images(self):
        """处理图片的后台线程"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            quality = int(float(self.quality_var.get()))
            keep_aspect = self.keep_aspect_var.get()
            
            if self.is_folder_var.get():
                # 处理文件夹
                recursive = self.recursive_var.get()
                self.resizer.resize_folder(
                    self.input_path.get(),
                    self.output_path.get(),
                    width, height,
                    keep_aspect, quality, recursive
                )
            else:
                # 处理单张图片
                self.resizer.resize_single_image(
                    self.input_path.get(),
                    self.output_path.get(),
                    width, height,
                    keep_aspect, quality
                )
            
            # 处理完成
            self.root.after(0, self.processing_completed)
            
        except Exception as e:
            self.root.after(0, lambda: self.processing_error(str(e)))
    
    def processing_completed(self):
        """处理完成"""
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        
        success_count = self.resizer.processed_count
        error_count = self.resizer.error_count
        
        if error_count == 0:
            self.status_label.config(text=f"处理完成！成功处理 {success_count} 张图片")
            messagebox.showinfo("完成", f"处理完成！\n成功处理: {success_count} 张图片")
        else:
            self.status_label.config(text=f"处理完成！成功: {success_count}，失败: {error_count}")
            error_details = "\n".join([f"{path}: {error}" for path, error in self.resizer.error_files[:5]])
            if len(self.resizer.error_files) > 5:
                error_details += f"\n... 还有 {len(self.resizer.error_files) - 5} 个错误"
            
            messagebox.showwarning("完成", 
                                 f"处理完成！\n成功处理: {success_count} 张图片\n"
                                 f"处理失败: {error_count} 张图片\n\n错误详情:\n{error_details}")
    
    def processing_error(self, error_message):
        """处理出错"""
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_label.config(text="处理失败")
        messagebox.showerror("错误", f"处理失败: {error_message}")
    
    def stop_processing(self):
        """停止处理（目前只是UI状态重置）"""
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_label.config(text="已停止")


def main():
    """主函数"""
    root = tk.Tk()
    app = ImageResizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 