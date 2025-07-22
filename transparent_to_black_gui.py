#!/usr/bin/env python3
"""
PNG透明像素转黑色GUI工具
提供图形界面来批量处理PNG图片，将透明像素转换为黑色
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from PIL import Image, ImageTk
import numpy as np
from transparent_to_black import process_transparent_to_black, batch_process_folder


class TransparentToBlackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG透明像素转黑色工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.recursive_var = tk.BooleanVar()
        self.processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件/文件夹选择", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入路径选择
        ttk.Label(file_frame, text="输入路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.input_path, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        input_button_frame = ttk.Frame(file_frame)
        input_button_frame.grid(row=0, column=2)
        ttk.Button(input_button_frame, text="选择文件", command=self.browse_input_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_button_frame, text="选择文件夹", command=self.browse_input_folder).pack(side=tk.LEFT)
        
        # 输出路径选择
        ttk.Label(file_frame, text="输出路径:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.output_path, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="选择文件夹", command=self.browse_output_folder).grid(row=1, column=2, pady=(10, 0))
        
        # 选项区域
        options_frame = ttk.LabelFrame(main_frame, text="处理选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="递归处理子文件夹", variable=self.recursive_var).pack(anchor=tk.W)
        
        # 说明文本
        info_text = ("说明：\n"
                    "• 选择单个PNG文件或包含PNG文件的文件夹\n"
                    "• 工具会将PNG图片中的透明像素转换为黑色\n"
                    "• 如果不指定输出路径，会在原文件名后添加'_no_transparent'后缀\n"
                    "• 没有透明像素的图片会被跳过")
        
        info_label = ttk.Label(options_frame, text=info_text, foreground="gray")
        info_label.pack(anchor=tk.W, pady=(10, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="开始处理", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="清除", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="打开输出文件夹", command=self.open_output_folder).pack(side=tk.LEFT)
        
        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def browse_input_file(self):
        """浏览选择输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择PNG图片",
            filetypes=[
                ("PNG文件", "*.png"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.input_path.set(file_path)
            self.log(f"选择输入文件: {file_path}")
    
    def browse_input_folder(self):
        """浏览选择输入文件夹"""
        folder_path = filedialog.askdirectory(title="选择包含PNG文件的文件夹")
        if folder_path:
            self.input_path.set(folder_path)
            self.log(f"选择输入文件夹: {folder_path}")
    
    def browse_output_folder(self):
        """浏览选择输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_path.set(folder_path)
            self.log(f"选择输出文件夹: {folder_path}")
    
    def clear_all(self):
        """清除所有内容"""
        self.input_path.set("")
        self.output_path.set("")
        self.recursive_var.set(False)
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("准备就绪")
        self.log("已清除所有内容")
    
    def open_output_folder(self):
        """打开输出文件夹"""
        output_path = self.output_path.get()
        if not output_path:
            messagebox.showwarning("警告", "请先指定输出文件夹")
            return
        
        if not os.path.exists(output_path):
            messagebox.showwarning("警告", "输出文件夹不存在")
            return
        
        # 在不同操作系统上打开文件夹
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_path])
            else:  # Linux
                subprocess.run(["xdg-open", output_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
    
    def log(self, message):
        """添加日志信息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_processing(self):
        """开始处理"""
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return
        
        input_path = self.input_path.get().strip()
        if not input_path:
            messagebox.showwarning("警告", "请选择输入文件或文件夹")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("错误", "输入路径不存在")
            return
        
        # 在新线程中处理，避免界面卡顿
        self.processing = True
        self.process_button.config(state="disabled")
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        """处理文件的线程函数"""
        try:
            input_path = self.input_path.get().strip()
            output_path = self.output_path.get().strip() if self.output_path.get().strip() else None
            recursive = self.recursive_var.get()
            
            self.log("=" * 50)
            self.log("开始处理...")
            self.status_var.set("正在处理...")
            
            if os.path.isfile(input_path):
                # 处理单个文件
                self.log(f"处理单个文件: {os.path.basename(input_path)}")
                self.progress_var.set(50)
                
                result = process_transparent_to_black(input_path, output_path)
                
                if result:
                    self.log(f"✓ 处理成功: {result}")
                    self.progress_var.set(100)
                    self.status_var.set("处理完成")
                    messagebox.showinfo("成功", f"文件处理完成！\n输出: {result}")
                else:
                    self.log("- 文件无需处理或处理失败")
                    self.progress_var.set(100)
                    self.status_var.set("处理完成")
                    messagebox.showinfo("完成", "文件无需处理（没有透明像素）")
            
            elif os.path.isdir(input_path):
                # 处理文件夹
                self.log(f"处理文件夹: {input_path}")
                self.log(f"递归处理: {'是' if recursive else '否'}")
                if output_path:
                    self.log(f"输出文件夹: {output_path}")
                
                # 重定向输出到GUI
                original_print = print
                def gui_print(*args, **kwargs):
                    message = " ".join(str(arg) for arg in args)
                    self.log(message)
                
                # 临时替换print函数
                import builtins
                builtins.print = gui_print
                
                try:
                    success, skip, error = batch_process_folder(input_path, output_path, recursive)
                    
                    self.progress_var.set(100)
                    self.status_var.set("批处理完成")
                    
                    result_msg = (f"批处理完成！\n\n"
                                f"成功处理: {success} 个文件\n"
                                f"跳过文件: {skip} 个文件\n"
                                f"处理失败: {error} 个文件")
                    
                    if error > 0:
                        messagebox.showwarning("完成（有错误）", result_msg)
                    else:
                        messagebox.showinfo("成功", result_msg)
                
                finally:
                    # 恢复原始print函数
                    builtins.print = original_print
            
        except Exception as e:
            self.log(f"处理过程中发生错误: {str(e)}")
            self.status_var.set("处理失败")
            messagebox.showerror("错误", f"处理失败: {str(e)}")
        
        finally:
            self.processing = False
            self.process_button.config(state="normal")


def main():
    """主函数"""
    root = tk.Tk()
    app = TransparentToBlackGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()