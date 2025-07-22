import argparse
import os
import zipfile
from os.path import join
import re

from result_process_lib.dir_helper import get_dirs
from result_process_lib.excel_parse import parse_result, write_result


def zip_dir(zipf, folder_path, arcname):
    """将文件夹添加到压缩包中并设置对应的相对路径"""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 获取文件的绝对路径
            file_path = join(root, file)
            # 获取文件在压缩包中的路径（相对路径）
            arc_path = os.path.join(arcname, os.path.relpath(file_path, folder_path))
            # 将文件添加到压缩包
            zipf.write(file_path, arcname=arc_path)
            print(f"Add file: {arc_path}")


def create_zip_file(zip_file_path, run_path, result_path, relative_path):
    """创建压缩包"""
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zip_dir(zipf, run_path, os.path.join(relative_path, 'run'))
        zip_dir(zipf, result_path, os.path.join(relative_path, 'result'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_path", type=str, required=True,
                        help="Base directory containing run folders")
    args = parser.parse_args()
    
    # 使用命令行参数的基础路径
    base_path = args.base_path
    
    # 检查基础路径是否存在
    if not os.path.exists(base_path):
        print(f"错误: 基础路径 {base_path} 不存在")
        exit(1)
    
    # 获取所有run文件夹
    all_dirs = get_dirs(base_path)
    run_dirs = [d for d in all_dirs if re.match(r'^run\d+$', d)]
    run_dirs.sort(key=lambda x: int(x.replace('run', '')))  # 按数字排序
    
    print(f"找到的run文件夹: {run_dirs}")
    all_data_list = []
    # 遍历每个run文件夹
    for run_folder in run_dirs:
        run_num = run_folder.replace('run', '')
        print(f"\n处理 {run_folder} (run_num: {run_num})")
        
        run_dir = f"{base_path}/{run_folder}/runs"
        result_dir = f"{base_path}/{run_folder}/results"
        final_result_dir = f"{base_path}/{run_folder}/final-result"
        
        # 检查必要的目录是否存在
        if not os.path.exists(result_dir):
            print(f"警告: {result_dir} 不存在，跳过 {run_folder}")
            continue
            
        os.makedirs(final_result_dir, exist_ok=True)
        
        try:
            data_list = parse_result(result_dir, final_result_dir)
            all_data_list.extend(data_list)
            print(f"成功处理 {run_folder}")
        except Exception as e:
            print(f"处理 {run_folder} 时出错: {e}")
    
    write_result(all_data_list, base_path)
    print("\n所有run文件夹处理完成")
    exit(0)

    # 注释掉原来的压缩逻辑，如果需要可以取消注释
    # for model in get_dirs(run_dir):
    #     model_run_dir = join(run_dir, model)
    #     model_result_dir = join(result_dir, model)
    #     for dataset in get_dirs(model_run_dir):
    #         dataset_run_dir = join(model_run_dir, dataset)
    #         dataset_result_dir = join(model_result_dir, dataset)
    #         final_result_path = join(final_result_dir, model, f'{model}-{dataset}.zip')
    #         os.makedirs(join(final_result_dir, model), exist_ok=True)
    #         create_zip_file(final_result_path, dataset_run_dir, dataset_result_dir,
    #                         os.path.join(model, dataset))
