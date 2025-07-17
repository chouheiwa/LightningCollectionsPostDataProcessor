# 文件重组工具使用说明

## 概述

文件重组工具用于处理包含多个结构相同子目录的文件夹，这些子目录中都包含 `run0`、`run1`、`run2`、`run3`、`run4` 文件夹。该工具可以将这些 run 文件夹提取出来，并将它们的内容合并到一个新的组织结构中。**注意：工具使用移动操作而非复制操作，因此会修改原始文件结构。**

## 功能特点

- **自动扫描**: 自动扫描源目录中的所有子目录，找到包含 run0-run4 的目录
- **结构重组**: 将分散在不同子目录中的 run 文件夹内容合并到统一的结构中
- **高效移动**: 使用移动操作而非复制操作，处理大文件时更快速
- **冲突处理**: 智能处理文件名冲突，自动重命名冲突文件
- **预览模式**: 支持预览模式，可以在实际执行前查看操作结果
- **日志记录**: 详细的操作日志，方便跟踪处理过程
- **GUI界面**: 提供图形用户界面，操作更加直观

## 原始结构示例

```
source_directory/
├── experiment_1/
│   ├── run0/
│   │   ├── data.txt
│   │   └── results.log
│   ├── run1/
│   │   ├── data.txt
│   │   └── results.log
│   └── run2/
│       ├── data.txt
│       └── results.log
├── experiment_2/
│   ├── run0/
│   │   ├── data.txt
│   │   └── results.log
│   ├── run1/
│   │   ├── data.txt
│   │   └── results.log
│   └── run3/
│       ├── data.txt
│       └── results.log
└── experiment_3/
    ├── run0/
    │   ├── data.txt
    │   └── results.log
    └── run4/
        ├── data.txt
        └── results.log
```

## 重组后结构

### 保留源目录结构模式（默认）

```
reorganized/
├── run0/
│   ├── experiment_1/
│   │   ├── data.txt
│   │   └── results.log
│   ├── experiment_2/
│   │   ├── data.txt
│   │   └── results.log
│   └── experiment_3/
│       ├── data.txt
│       └── results.log
├── run1/
│   ├── experiment_1/
│   │   ├── data.txt
│   │   └── results.log
│   └── experiment_2/
│       ├── data.txt
│       └── results.log
├── run2/
│   └── experiment_1/
│       ├── data.txt
│       └── results.log
├── run3/
│   └── experiment_2/
│       ├── data.txt
│       └── results.log
└── run4/
    └── experiment_3/
        ├── data.txt
        └── results.log
```

### 直接合并模式（推荐）

```
reorganized/
├── run0/
│   ├── runs/
│   │   └── (合并了所有experiment_*/run0/runs的内容)
│   └── results/
│       └── (合并了所有experiment_*/run0/results的内容)
├── run1/
│   ├── runs/
│   │   └── (合并了所有experiment_*/run1/runs的内容)
│   └── results/
│       └── (合并了所有experiment_*/run1/results的内容)
├── run2/
│   ├── runs/
│   └── results/
├── run3/
│   ├── runs/
│   └── results/
└── run4/
    ├── runs/
    └── results/
```

## 使用方法

### 1. 命令行版本

#### 基本用法

```bash
python file_reorganizer.py /path/to/source/directory
```

#### 完整参数

```bash
python file_reorganizer.py /path/to/source/directory \
    --output /path/to/output/directory \
    --dry-run \
    --keep-original \
    --direct-merge
```

#### 参数说明

- `source_dir`: 源目录路径（必需）
- `-o, --output`: 输出目录路径（可选，默认为源目录下的 "reorganized" 文件夹）
- `-d, --dry-run`: 预览模式，只显示将要执行的操作而不实际执行
- `-p, --preview`: 预览目录结构
- `--keep-original`: 保留原始目录结构（不删除源目录）
- `--direct-merge`: 直接合并run文件夹内容，不保留源目录层次（推荐）

#### 使用示例

1. **预览操作**：
   ```bash
   python file_reorganizer.py /path/to/data --preview
   ```

2. **预览模式执行**：
   ```bash
   python file_reorganizer.py /path/to/data --dry-run
   ```

3. **直接合并模式执行（推荐）**：
   ```bash
   python file_reorganizer.py /path/to/data --direct-merge
   ```

4. **实际执行并保留原始目录**：
   ```bash
   python file_reorganizer.py /path/to/data --keep-original
   ```

5. **指定输出目录**：
   ```bash
   python file_reorganizer.py /path/to/data --output /path/to/output
   ```

6. **完整示例（直接合并模式）**：
   ```bash
   python file_reorganizer.py /path/to/data --direct-merge --keep-original --output /path/to/output
   ```

### 2. GUI版本

#### 启动GUI

```bash
python file_reorganizer_gui.py
```

#### GUI操作步骤

1. **选择源目录**: 点击"选择"按钮选择包含子目录的源目录
2. **选择输出目录**: 点击"选择"按钮选择输出目录（可选，默认为源目录下的 "reorganized" 文件夹）
3. **设置选项**:
   - 勾选"保留原始目录结构"可以保留源目录不被删除
   - 勾选"预览模式"可以只预览操作而不实际执行
   - 勾选"直接合并模式"将直接合并run文件夹内容（推荐，默认开启）
4. **预览结构**: 点击"预览结构"按钮查看将要创建的目录结构
5. **开始重组**: 点击"开始重组"按钮执行文件重组操作

#### GUI功能

- **实时日志**: 操作过程中的详细日志会实时显示在界面中
- **状态栏**: 显示当前操作状态
- **进度跟踪**: 可以实时查看操作进度
- **错误处理**: 遇到错误时会弹出对话框提示

## 注意事项

1. **重要警告**: 工具使用移动操作，会修改原始文件结构。执行前请务必备份重要数据！
2. **备份数据**: 在执行实际操作前，建议备份重要数据
3. **权限检查**: 确保有足够的权限读取源目录和写入输出目录
4. **磁盘空间**: 由于使用移动操作，不需要额外的磁盘空间
5. **文件名冲突**: 工具会自动处理文件名冲突，为冲突文件添加前缀
6. **日志文件**: 操作日志会保存在 `file_reorganizer.log` 文件中
7. **不可逆操作**: 移动操作是不可逆的，请谨慎使用

## 错误处理

工具包含完善的错误处理机制：

- **目录不存在**: 会提示源目录不存在
- **权限不足**: 会提示权限错误
- **磁盘空间不足**: 会提示磁盘空间不足
- **文件正在使用**: 会提示文件被占用

## 日志级别

- **INFO**: 一般信息，如发现的目录、创建的文件夹等
- **WARNING**: 警告信息，如没有找到目标目录等
- **ERROR**: 错误信息，如操作失败等

## 技术要求

- Python 3.6+
- 标准库依赖：`os`, `shutil`, `pathlib`, `argparse`, `logging`
- GUI版本额外需要：`tkinter`

## 故障排除

### 常见问题

1. **找不到 run0-run4 文件夹**
   - 检查源目录结构是否正确
   - 确认子目录中确实包含名为 run0-run4 的文件夹

2. **权限错误**
   - 检查对源目录的读取权限
   - 检查对输出目录的写入权限

3. **磁盘空间不足**
   - 清理磁盘空间
   - 选择其他有足够空间的输出目录

4. **GUI无法启动**
   - 确认系统支持 tkinter
   - 检查Python版本是否支持

### 获取帮助

如果遇到问题，可以：
1. 查看 `file_reorganizer.log` 日志文件
2. 使用 `--dry-run` 参数预览操作
3. 使用 `--preview` 参数查看目录结构 