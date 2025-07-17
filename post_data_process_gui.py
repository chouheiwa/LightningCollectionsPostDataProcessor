import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import re
from datetime import datetime
from result_process_lib.dir_helper import get_dirs
from result_process_lib.excel_parse import parse_result, write_result


class DataProcessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("数据处理工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 默认基础路径
        self.base_path = tk.StringVar(value="/Users/chouheiwa/Downloads/data_results_current")
        self.run_folders = []
        self.processing = False
        
        self.setup_ui()
        self.refresh_run_folders()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 路径选择区域
        path_frame = ttk.LabelFrame(main_frame, text="路径设置", padding="5")
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_frame, text="基础路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.base_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(path_frame, text="浏览", command=self.browse_path).grid(row=0, column=2)
        ttk.Button(path_frame, text="刷新", command=self.refresh_run_folders).grid(row=0, column=3, padx=(5, 0))
        
        # Run文件夹列表区域
        list_frame = ttk.LabelFrame(main_frame, text="Run文件夹列表", padding="5")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 状态标签
        self.status_label = ttk.Label(list_frame, text="准备就绪")
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 创建Treeview来显示run文件夹
        columns = ('folder', 'status', 'results_exist')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 定义列标题
        self.tree.heading('folder', text='Run文件夹')
        self.tree.heading('status', text='状态')
        self.tree.heading('results_exist', text='Results目录')
        
        # 设置列宽
        self.tree.column('folder', width=150)
        self.tree.column('status', width=100)
        self.tree.column('results_exist', width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="开始处理", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT, padx=(0, 10))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(button_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 清除日志按钮
        ttk.Button(log_frame, text="清除日志", command=self.clear_log).grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
    
    def browse_path(self):
        """浏览选择基础路径"""
        path = filedialog.askdirectory(initialdir=self.base_path.get())
        if path:
            self.base_path.set(path)
            self.refresh_run_folders()
    
    def refresh_run_folders(self):
        """刷新run文件夹列表"""
        try:
            # 清空现有列表
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            base_path = self.base_path.get()
            if not os.path.exists(base_path):
                self.status_label.config(text="路径不存在")
                return
            
            # 获取所有run文件夹
            all_dirs = get_dirs(base_path)
            self.run_folders = [d for d in all_dirs if re.match(r'^run\d+$', d)]
            self.run_folders.sort(key=lambda x: int(x.replace('run', '')))
            
            # 添加到树视图
            for folder in self.run_folders:
                results_path = os.path.join(base_path, folder, "results")
                results_exist = "✓" if os.path.exists(results_path) else "✗"
                
                item = self.tree.insert('', 'end', values=(folder, '待处理', results_exist))
            
            self.status_label.config(text=f"找到 {len(self.run_folders)} 个run文件夹")
            self.log_message(f"刷新完成，找到 {len(self.run_folders)} 个run文件夹: {', '.join(self.run_folders)}")
            
        except Exception as e:
            self.status_label.config(text="刷新失败")
            self.log_message(f"刷新失败: {str(e)}")
    
    def select_all(self):
        """全选所有项目"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def deselect_all(self):
        """取消全选"""
        self.tree.selection_remove(self.tree.selection())
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
    
    def start_processing(self):
        """开始处理数据"""
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请等待...")
            return
        
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择要处理的run文件夹")
            return
        
        # 在新线程中处理，避免界面冻结
        self.processing = True
        self.process_button.config(text="处理中...", state='disabled')
        
        threading.Thread(target=self.process_data, args=(selected_items,), daemon=True).start()
    
    def process_data(self, selected_items):
        """处理数据的主要逻辑"""
        try:
            base_path = self.base_path.get()
            total_items = len(selected_items)
            
            self.log_message(f"开始处理 {total_items} 个run文件夹...")

            all_data_list = []
            for i, item in enumerate(selected_items):
                folder = self.tree.item(item, 'values')[0]
                
                # 更新状态
                self.tree.item(item, values=(folder, '处理中...', self.tree.item(item, 'values')[2]))
                self.log_message(f"正在处理 {folder}...")
                
                try:
                    # 构造路径
                    result_dir = os.path.join(base_path, folder, "results")
                    final_result_dir = os.path.join(base_path, folder, "final-result")
                    
                    # 检查results目录是否存在
                    if not os.path.exists(result_dir):
                        self.tree.item(item, values=(folder, '跳过-无results', self.tree.item(item, 'values')[2]))
                        self.log_message(f"警告: {result_dir} 不存在，跳过 {folder}")
                        continue
                    
                    # 创建final-result目录
                    os.makedirs(final_result_dir, exist_ok=True)
                    
                    # 调用处理函数
                    data_list = parse_result(result_dir, final_result_dir)
                    # 删除data_list中的最后一行
                    data_list.pop()
                    all_data_list.extend(data_list)
                    
                    # 更新状态
                    self.tree.item(item, values=(folder, '完成', self.tree.item(item, 'values')[2]))
                    self.log_message(f"成功处理 {folder}")
                    
                except Exception as e:
                    self.tree.item(item, values=(folder, '错误', self.tree.item(item, 'values')[2]))
                    self.log_message(f"处理 {folder} 时出错: {str(e)}")
                
                # 更新进度条
                progress = ((i + 1) / total_items) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            write_result(all_data_list, base_path)

            self.log_message("所有选定的run文件夹处理完成!")
            messagebox.showinfo("完成", "数据处理完成!")
            
        except Exception as e:
            self.log_message(f"处理过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"处理失败: {str(e)}")
        
        finally:
            # 重置UI状态
            self.processing = False
            self.process_button.config(text="开始处理", state='normal')
            self.progress_var.set(0)


def main():
    root = tk.Tk()
    app = DataProcessGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main() 