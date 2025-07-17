#!/usr/bin/env python3
"""
文件重组工具 - GUI版本
用于处理多个子目录中的run0-run4文件夹的提取和合并
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from datetime import datetime

# 导入我们的文件重组类
from file_reorganizer import FileReorganizer

class FileReorganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件重组工具")
        self.root.geometry("800x600")
        
        # 设置窗口图标（如果有的话）
        self.root.resizable(True, True)
        
        # 创建主框架
        self.setup_ui()
        
        # 存储选择的目录
        self.source_dir = None
        self.output_dir = None
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="文件重组工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 说明文本
        description = (
            "此工具用于重组包含run0-run4文件夹的目录结构。\n"
            "它会扫描源目录中的所有子目录，找到其中的run0-run4文件夹，\n"
            "并将它们的内容合并到一个新的组织结构中。\n"
            "直接合并模式：将各个run文件夹的内容直接合并（推荐）。\n"
            "警告：工具使用移动操作，会修改原始文件结构，请先备份！"
        )
        desc_label = ttk.Label(main_frame, text=description, justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # 源目录选择
        ttk.Label(main_frame, text="源目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar()
        self.source_entry = ttk.Entry(main_frame, textvariable=self.source_var, width=50)
        self.source_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="选择", command=self.select_source_dir).grid(row=2, column=2, pady=5)
        
        # 输出目录选择
        ttk.Label(main_frame, text="输出目录:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        self.output_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="选择", command=self.select_output_dir).grid(row=3, column=2, pady=5)
        
        # 选项框架
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 选项
        self.keep_original_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="保留原始目录结构", variable=self.keep_original_var).grid(row=0, column=0, sticky=tk.W)
        
        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="预览模式（不实际执行）", variable=self.dry_run_var).grid(row=1, column=0, sticky=tk.W)
        
        self.direct_merge_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="直接合并模式（推荐）", variable=self.direct_merge_var).grid(row=2, column=0, sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 按钮
        ttk.Button(button_frame, text="预览结构", command=self.preview_structure).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="开始重组", command=self.start_reorganization).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def select_source_dir(self):
        """选择源目录"""
        dir_path = filedialog.askdirectory(title="选择源目录")
        if dir_path:
            self.source_var.set(dir_path)
            self.source_dir = dir_path
            self.log(f"已选择源目录: {dir_path}")
            
            # 如果没有设置输出目录，默认设置为源目录下的reorganized文件夹
            if not self.output_var.get():
                default_output = os.path.join(dir_path, "reorganized")
                self.output_var.set(default_output)
                self.output_dir = default_output
    
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_var.set(dir_path)
            self.output_dir = dir_path
            self.log(f"已选择输出目录: {dir_path}")
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def preview_structure(self):
        """预览目录结构"""
        if not self.validate_inputs():
            return
        
        try:
            self.status_var.set("正在预览目录结构...")
            self.log("开始预览目录结构...")
            
            reorganizer = FileReorganizer(
                source_dir=self.source_dir,
                output_dir=self.output_dir,
                dry_run=True
            )
            
            found_dirs = reorganizer.scan_directories()
            
            if not found_dirs:
                self.log("没有找到包含run0-run4的子目录")
                self.status_var.set("预览完成 - 没有找到目标目录")
                return
            
            self.log(f"发现 {len(found_dirs)} 个包含run文件夹的目录")
            self.log("\n发现的目录结构：")
            
            for parent_dir, run_paths in found_dirs.items():
                self.log(f"  {parent_dir}/")
                for run_path in run_paths:
                    self.log(f"    └── {run_path.name}/")
                    if run_path.exists():
                        for item in run_path.iterdir():
                            self.log(f"        └── {item.name}")
            
            self.log(f"\n将要创建的输出结构：")
            self.log(f"  {reorganizer.output_dir}/")
            for run_folder in reorganizer.run_folders:
                self.log(f"    └── {run_folder}/")
                for parent_dir in found_dirs.keys():
                    self.log(f"        └── {parent_dir}/")
            
            self.status_var.set("预览完成")
            
        except Exception as e:
            self.log(f"预览失败: {str(e)}")
            self.status_var.set("预览失败")
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def validate_inputs(self):
        """验证输入"""
        if not self.source_dir or not os.path.exists(self.source_dir):
            messagebox.showerror("错误", "请选择有效的源目录")
            return False
        
        if not self.output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return False
        
        return True
    
    def start_reorganization(self):
        """开始重组操作"""
        if not self.validate_inputs():
            return
        
        # 确认对话框
        if not self.dry_run_var.get():
            warning_message = (
                "确定要执行文件重组操作吗？\n\n"
                "⚠️ 重要警告：\n"
                "• 此操作使用移动而非复制，会修改原始文件结构\n"
                "• 操作不可逆，请确保已经备份重要数据\n"
                "• 如果不确定，请先使用预览模式查看结果\n\n"
                "是否继续？"
            )
            if not messagebox.askyesno("确认操作", warning_message):
                return
        
        # 在新线程中运行重组操作
        self.reorganization_thread = threading.Thread(target=self.run_reorganization)
        self.reorganization_thread.daemon = True
        self.reorganization_thread.start()
    
    def run_reorganization(self):
        """运行重组操作（在后台线程中）"""
        try:
            self.status_var.set("正在执行文件重组...")
            self.log("开始文件重组操作...")
            
            # 创建重组器实例
            reorganizer = FileReorganizer(
                source_dir=self.source_dir,
                output_dir=self.output_dir,
                dry_run=self.dry_run_var.get()
            )
            
            # 重定向日志到GUI
            class GUILogHandler:
                def __init__(self, gui):
                    self.gui = gui
                
                def info(self, message):
                    self.gui.log(f"INFO: {message}")
                
                def warning(self, message):
                    self.gui.log(f"WARNING: {message}")
                
                def error(self, message):
                    self.gui.log(f"ERROR: {message}")
            
            reorganizer.logger = GUILogHandler(self)
            
            # 执行重组
            reorganizer.reorganize(
                clean_original=not self.keep_original_var.get(),
                direct_merge=self.direct_merge_var.get()
            )
            
            self.status_var.set("重组完成")
            self.log("文件重组完成！")
            
            if not self.dry_run_var.get():
                messagebox.showinfo("成功", "文件重组完成！")
            
        except Exception as e:
            self.log(f"重组失败: {str(e)}")
            self.status_var.set("重组失败")
            messagebox.showerror("错误", f"重组失败: {str(e)}")


def main():
    root = tk.Tk()
    app = FileReorganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 