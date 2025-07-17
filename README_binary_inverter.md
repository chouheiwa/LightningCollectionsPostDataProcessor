# 二值图片反转工具

这是一个用于反转二值图片的Python工具，提供命令行和图形界面两种使用方式。

## 功能特点

- 支持多种图片格式（PNG、JPEG、BMP、TIFF等）
- 自动检测并处理非标准二值图（自动进行二值化）
- 提供命令行工具和图形界面两种使用方式
- 支持批量处理和实时预览

## 安装依赖

在运行脚本之前，请确保安装了必要的Python库：

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install Pillow numpy
```

## 使用方法

### 方法1：命令行工具

使用 `binary_image_inverter.py` 脚本：

```bash
# 基本使用
python binary_image_inverter.py input_image.png

# 指定输出文件
python binary_image_inverter.py input_image.png -o output_image.png

# 详细输出
python binary_image_inverter.py input_image.png -v
```

**参数说明：**
- `input`: 输入图片路径（必需）
- `-o, --output`: 输出图片路径（可选，默认在输入文件名后加_inverted）
- `-v, --verbose`: 详细输出模式

### 方法2：图形界面工具

使用 `binary_image_inverter_gui.py` 脚本：

```bash
python binary_image_inverter_gui.py
```

图形界面操作步骤：
1. 点击"浏览"按钮选择输入图片
2. 系统会自动生成输出路径，也可以手动指定
3. 点击"反转图片"按钮进行处理
4. 在预览区域查看反转效果
5. 点击"保存"按钮保存结果

## 工作原理

1. **图片读取**: 使用PIL库读取输入图片
2. **格式转换**: 将图片转换为灰度模式
3. **二值化检查**: 检查图片是否为标准二值图
4. **自动二值化**: 如果不是二值图，使用阈值127进行二值化
5. **像素反转**: 将像素值反转（0变255，255变0）
6. **结果保存**: 保存反转后的图片

## 示例

假设你有一个二值图片 `binary_image.png`，其中白色区域表示前景，黑色区域表示背景。

使用命令行工具：
```bash
python binary_image_inverter.py binary_image.png
```

这会生成一个名为 `binary_image_inverted.png` 的文件，其中原来的白色区域变为黑色，黑色区域变为白色。

## 支持的图片格式

- PNG
- JPEG/JPG
- BMP
- TIFF
- GIF
- 以及其他PIL支持的格式

## 注意事项

1. 输入图片最好是标准的二值图（只有黑白两种颜色）
2. 如果输入的不是二值图，工具会自动进行二值化处理
3. 输出图片会保存为灰度格式
4. 确保有足够的磁盘空间来保存输出图片

## 错误处理

- 如果输入文件不存在，会显示错误信息
- 如果图片格式不支持，会尝试转换或报错
- 如果保存失败，会显示具体的错误原因

## 系统要求

- Python 3.7或更高版本
- PIL (Pillow) 9.0.0或更高版本
- NumPy 1.21.0或更高版本
- tkinter（GUI版本需要，通常随Python安装） 