#!/usr/bin/env python3
"""
文件重组工具
用于处理多个子目录中的run0-run4文件夹的提取和合并
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List, Dict
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_reorganizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileReorganizer:
    def __init__(self, source_dir: str, output_dir: str = None, dry_run: bool = False):
        """
        初始化文件重组器
        
        Args:
            source_dir: 源目录路径
            output_dir: 输出目录路径，如果为None则在源目录创建reorganized文件夹
            dry_run: 是否只是预览操作而不实际执行
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir) if output_dir else self.source_dir / "reorganized"
        self.dry_run = dry_run
        self.run_folders = [f"run{i}" for i in range(5)]  # run0-run4
        self.logger = logger  # 添加logger属性
        
        if not self.source_dir.exists():
            raise ValueError(f"源目录不存在: {self.source_dir}")
    
    def _safe_move(self, src: Path, dest: Path):
        """
        安全的目录移动，处理目标已存在的情况
        
        Args:
            src: 源目录
            dest: 目标目录
        """
        try:
            if dest.exists():
                # 如果目标已存在，需要合并内容
                self._merge_directories(src, dest)
                # 合并完成后删除源目录
                shutil.rmtree(src)
            else:
                # 直接移动
                shutil.move(str(src), str(dest))
        except Exception as e:
            self.logger.warning(f"移动失败，尝试合并: {src} -> {dest}, 错误: {e}")
            # 如果移动失败，尝试合并
            self._merge_directories(src, dest)
            # 合并完成后删除源目录
            if src.exists():
                shutil.rmtree(src)
    
    def scan_directories(self) -> Dict[str, List[Path]]:
        """
        扫描源目录，找到所有包含run0-run4的子目录
        
        Returns:
            字典，键为子目录名，值为找到的run文件夹路径列表
        """
        found_dirs = {}
        
        for item in self.source_dir.iterdir():
            if item.is_dir():
                run_paths = []
                for run_folder in self.run_folders:
                    run_path = item / run_folder
                    if run_path.exists() and run_path.is_dir():
                        run_paths.append(run_path)
                
                if run_paths:
                    found_dirs[item.name] = run_paths
                    logger.info(f"在 {item.name} 中找到 {len(run_paths)} 个run文件夹")
        
        return found_dirs
    
    def create_output_structure(self):
        """创建输出目录结构"""
        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 为每个run文件夹创建对应的输出目录
            for run_folder in self.run_folders:
                run_output_dir = self.output_dir / run_folder
                run_output_dir.mkdir(exist_ok=True)
                logger.info(f"创建输出目录: {run_output_dir}")
        else:
            logger.info(f"[DRY RUN] 将创建输出目录: {self.output_dir}")
            for run_folder in self.run_folders:
                logger.info(f"[DRY RUN] 将创建子目录: {self.output_dir / run_folder}")
    
    def merge_run_folders(self, found_dirs: Dict[str, List[Path]], direct_merge: bool = False):
        """
        合并所有run文件夹的内容
        
        Args:
            found_dirs: 扫描到的目录信息
            direct_merge: 是否直接合并内容，而不保留源目录结构
        """
        for parent_dir, run_paths in found_dirs.items():
            logger.info(f"处理来自 {parent_dir} 的run文件夹...")
            
            for run_path in run_paths:
                run_name = run_path.name
                target_dir = self.output_dir / run_name
                
                if direct_merge:
                    # 直接合并模式：将内容直接复制到run文件夹下
                    if not self.dry_run:
                        target_dir.mkdir(parents=True, exist_ok=True)
                        
                        # 复制run文件夹的内容
                        if run_path.exists():
                            for item in run_path.iterdir():
                                dest_path = target_dir / item.name
                                if item.is_dir():
                                    if dest_path.exists():
                                        # 如果目标目录已存在，递归合并
                                        self._merge_directories(item, dest_path)
                                    else:
                                        # 使用安全的移动方法
                                        self._safe_move(item, dest_path)
                                else:
                                    # 处理文件名冲突
                                    if dest_path.exists():
                                        # 为冲突文件添加源目录前缀
                                        dest_path = target_dir / f"{parent_dir}_{item.name}"
                                    shutil.move(str(item), str(dest_path))
                                logger.info(f"移动: {item} -> {dest_path}")
                    else:
                        logger.info(f"[DRY RUN] 将创建目录: {target_dir}")
                        if run_path.exists():
                            for item in run_path.iterdir():
                                dest_path = target_dir / item.name
                                logger.info(f"[DRY RUN] 将移动: {item} -> {dest_path}")
                else:
                    # 保留源目录结构模式（原有功能）
                    source_subdir = target_dir / parent_dir
                    
                    if not self.dry_run:
                        source_subdir.mkdir(parents=True, exist_ok=True)
                        
                        # 复制run文件夹的内容
                        if run_path.exists():
                            for item in run_path.iterdir():
                                dest_path = source_subdir / item.name
                                if item.is_dir():
                                    self._safe_move(item, dest_path)
                                else:
                                    shutil.move(str(item), str(dest_path))
                                logger.info(f"移动: {item} -> {dest_path}")
                    else:
                        logger.info(f"[DRY RUN] 将创建目录: {source_subdir}")
                        if run_path.exists():
                            for item in run_path.iterdir():
                                dest_path = source_subdir / item.name
                                logger.info(f"[DRY RUN] 将移动: {item} -> {dest_path}")
    
    def _merge_directories(self, src_dir: Path, dest_dir: Path):
        """
        递归合并两个目录，使用移动操作
        
        Args:
            src_dir: 源目录
            dest_dir: 目标目录
        """
        for item in src_dir.iterdir():
            dest_path = dest_dir / item.name
            if item.is_dir():
                if dest_path.exists():
                    # 递归合并子目录
                    self._merge_directories(item, dest_path)
                    # 合并完成后删除源子目录
                    shutil.rmtree(item)
                else:
                    # 直接移动子目录
                    shutil.move(str(item), str(dest_path))
            else:
                if dest_path.exists():
                    # 处理文件名冲突，添加源目录前缀
                    try:
                        parent_name = src_dir.parent.parent.name  # 获取原始源目录名
                        dest_path = dest_dir / f"{parent_name}_{item.name}"
                    except:
                        # 如果无法获取父目录名，使用时间戳
                        import time
                        timestamp = int(time.time())
                        dest_path = dest_dir / f"{timestamp}_{item.name}"
                
                # 移动文件
                shutil.move(str(item), str(dest_path))
            logger.info(f"移动: {item} -> {dest_path}")
    
    def clean_original_structure(self, found_dirs: Dict[str, List[Path]]):
        """
        清理原始目录结构
        
        Args:
            found_dirs: 扫描到的目录信息
        """
        if not self.dry_run:
            for parent_dir, _ in found_dirs.items():
                parent_path = self.source_dir / parent_dir
                if parent_path.exists():
                    shutil.rmtree(parent_path)
                    logger.info(f"删除原始目录: {parent_path}")
        else:
            for parent_dir, _ in found_dirs.items():
                parent_path = self.source_dir / parent_dir
                logger.info(f"[DRY RUN] 将删除目录: {parent_path}")
    
    def reorganize(self, clean_original: bool = True, direct_merge: bool = False):
        """
        执行文件重组
        
        Args:
            clean_original: 是否删除原始目录结构
            direct_merge: 是否直接合并内容，而不保留源目录结构
        """
        logger.info(f"开始重组目录: {self.source_dir}")
        logger.info(f"输出目录: {self.output_dir}")
        logger.info(f"干运行模式: {self.dry_run}")
        logger.info(f"直接合并模式: {direct_merge}")
        
        # 1. 扫描目录
        found_dirs = self.scan_directories()
        
        if not found_dirs:
            logger.warning("没有找到包含run0-run4的子目录")
            return
        
        logger.info(f"找到 {len(found_dirs)} 个包含run文件夹的目录")
        
        # 2. 创建输出结构
        self.create_output_structure()
        
        # 3. 合并run文件夹
        self.merge_run_folders(found_dirs, direct_merge)
        
        # 4. 清理原始结构（可选）
        if clean_original:
            self.clean_original_structure(found_dirs)
        
        logger.info("文件重组完成！")
    
    def preview(self):
        """预览将要执行的操作"""
        found_dirs = self.scan_directories()
        
        if not found_dirs:
            print("没有找到包含run0-run4的子目录")
            return
        
        print(f"\n发现的目录结构：")
        for parent_dir, run_paths in found_dirs.items():
            print(f"  {parent_dir}/")
            for run_path in run_paths:
                print(f"    └── {run_path.name}/")
                if run_path.exists():
                    for item in run_path.iterdir():
                        print(f"        └── {item.name}")
        
        print(f"\n将要创建的输出结构：")
        print(f"  {self.output_dir}/")
        for run_folder in self.run_folders:
            print(f"    └── {run_folder}/")
            for parent_dir in found_dirs.keys():
                print(f"        └── {parent_dir}/")


def main():
    parser = argparse.ArgumentParser(description="文件重组工具")
    parser.add_argument("source_dir", help="源目录路径")
    parser.add_argument("-o", "--output", help="输出目录路径")
    parser.add_argument("-d", "--dry-run", action="store_true", help="只预览操作，不实际执行")
    parser.add_argument("-p", "--preview", action="store_true", help="预览目录结构")
    parser.add_argument("--keep-original", action="store_true", help="保留原始目录结构")
    parser.add_argument("--direct-merge", action="store_true", help="直接合并run文件夹内容，不保留源目录层次")
    
    args = parser.parse_args()
    
    try:
        reorganizer = FileReorganizer(
            source_dir=args.source_dir,
            output_dir=args.output,
            dry_run=args.dry_run
        )
        
        if args.preview:
            reorganizer.preview()
        else:
            reorganizer.reorganize(
                clean_original=not args.keep_original,
                direct_merge=args.direct_merge
            )
            
    except Exception as e:
        logger.error(f"错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 