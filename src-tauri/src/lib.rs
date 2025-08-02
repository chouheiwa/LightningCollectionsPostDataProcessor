use tauri_plugin_dialog;
use std::path::Path;
use std::fs;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
struct RunFolderInfo {
    name: String,
    #[serde(rename = "hasResults")]
    has_results: bool,
    status: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ScanResult {
    folders: Vec<RunFolderInfo>,
    total: usize,
}

#[derive(Debug, Serialize, Deserialize)]
struct MetricData {
    model: String,
    dataset: String,
    #[serde(rename = "Miou")]
    miou: f64,
    #[serde(rename = "F1_score")]
    f1_score: f64,
    #[serde(rename = "Accuracy")]
    accuracy: f64,
    #[serde(rename = "Specificity")]
    specificity: f64,
    #[serde(rename = "Sensitivity")]
    sensitivity: f64,
    #[serde(rename = "DSC")]
    dsc: f64,
    #[serde(rename = "Precision")]
    precision: f64,
    #[serde(rename = "Parameters（M）")]
    parameters_m: f64,
    #[serde(rename = "FLOPS（G）")]
    flops_g: f64,
}

// 二进制图像反转处理
#[tauri::command]
async fn process_binary_images(files: Vec<String>) -> Result<String, String> {
    let python_script = "../python_version/binary_image_inverter.py";
    
    for file in files {
        let output = Command::new("python3")
            .arg(python_script)
            .arg(&file)
            .output()
            .map_err(|e| format!("执行失败: {}", e))?;
            
        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(format!("处理文件 {} 失败: {}", file, error));
        }
    }
    
    Ok("所有文件处理完成".to_string())
}

// 获取目录列表
fn get_dirs(path: &Path) -> Result<Vec<String>, String> {
    let mut dirs = Vec::new();
    
    if !path.exists() {
        return Err(format!("路径不存在: {}", path.display()));
    }
    
    let entries = fs::read_dir(path)
        .map_err(|e| format!("读取目录失败: {}", e))?;
    
    for entry in entries {
        let entry = entry.map_err(|e| format!("读取条目失败: {}", e))?;
        if entry.file_type().map_err(|e| format!("获取文件类型失败: {}", e))?.is_dir() {
            if let Some(name) = entry.file_name().to_str() {
                dirs.push(name.to_string());
            }
        }
    }
    
    Ok(dirs)
}

// 从数据集名称中提取数字
fn extract_dataset_number(dataset_name: &str) -> Result<i32, String> {
    let parts: Vec<&str> = dataset_name.split('-').collect();
    if parts.len() < 2 {
        return Err(format!("Invalid dataset name format: {}", dataset_name));
    }
    
    let number_part = parts[1];
    if number_part.chars().all(char::is_numeric) {
        number_part.parse::<i32>()
            .map_err(|e| format!("Failed to parse number: {}", e))
    } else {
        let underscore_parts: Vec<&str> = number_part.split('_').collect();
        underscore_parts[0].parse::<i32>()
            .map_err(|e| format!("Failed to parse number: {}", e))
    }
}



// 解析CSV数据
fn parse_csv_data(csv_path: &Path, model: &str, dataset: &str) -> Result<MetricData, String> {
    let file = fs::File::open(csv_path)
        .map_err(|e| format!("Failed to open CSV file: {}", e))?;
    
    let mut reader = csv::Reader::from_reader(file);
    let headers = reader.headers()
        .map_err(|e| format!("Failed to read CSV headers: {}", e))?
        .clone();
    
    let mut last_record = None;
    for result in reader.records() {
        let record = result.map_err(|e| format!("Failed to read CSV record: {}", e))?;
        last_record = Some(record);
    }
    
    let record = last_record.ok_or_else(|| "CSV file is empty".to_string())?;
    
    // 创建一个映射来查找列索引
    let mut header_map = std::collections::HashMap::new();
    for (i, header) in headers.iter().enumerate() {
        header_map.insert(header, i);
    }
    
    // 辅助函数来获取值
    let get_value = |key: &str| -> Result<f64, String> {
        let index = header_map.get(key)
            .ok_or_else(|| format!("Column '{}' not found", key))?;
        let value_str = record.get(*index)
            .ok_or_else(|| format!("Value at index {} not found", index))?;
        value_str.parse::<f64>()
            .map_err(|e| format!("Failed to parse '{}' as float: {}", value_str, e))
    };
    
    Ok(MetricData {
        model: model.to_string(),
        dataset: dataset.to_string(),
        miou: get_value("test/MeanIoU")? * 100.0,
        f1_score: get_value("test/BinaryF1Score")? * 100.0,
        accuracy: get_value("test/BinaryAccuracy")? * 100.0,
        specificity: get_value("test/BinarySpecificity")? * 100.0,
        sensitivity: get_value("test/BinaryRecall")? * 100.0,
        dsc: get_value("test/Dice")? * 100.0,
        precision: get_value("test/BinaryPrecision")? * 100.0,
        parameters_m: get_value("Parameters")? / 1e6,
        flops_g: get_value("FLOPs")? / 1e9,
    })
}

// 处理结果目录
fn parse_result(result_dir: &Path, _final_result_dir: &Path) -> Result<Vec<MetricData>, String> {
    let mut data_list = Vec::new();
    
    let models = get_dirs(result_dir)?;
    for model in models {
        let model_result_dir = result_dir.join(&model);
        let mut datasets = get_dirs(&model_result_dir)?;
        
        // 按数字排序数据集
        datasets.sort_by(|a, b| {
            let a_num = extract_dataset_number(a).unwrap_or(0);
            let b_num = extract_dataset_number(b).unwrap_or(0);
            a_num.cmp(&b_num)
        });
        
        for dataset in datasets {
            let dataset_result_csv = model_result_dir.join(&dataset).join("result").join("metrics.csv");
            if dataset_result_csv.exists() {
                match parse_csv_data(&dataset_result_csv, &model, &dataset) {
                    Ok(data) => data_list.push(data),
                    Err(e) => eprintln!("Warning: Failed to parse {}/{}: {}", model, dataset, e),
                }
            } else {
                eprintln!("Warning: metrics.csv not found for {}/{}", model, dataset);
            }
        }
    }
    
    Ok(data_list)
}

// 写入结果
fn write_result(data_list: &[MetricData], output_dir: &Path) -> Result<(), String> {
    fs::create_dir_all(output_dir)
        .map_err(|e| format!("Failed to create output directory: {}", e))?;
    
    let output_path = output_dir.join("final_result.csv");
    let file = fs::File::create(&output_path)
        .map_err(|e| format!("Failed to create output file: {}", e))?;
    
    let mut writer = csv::Writer::from_writer(file);
    
    for data in data_list {
        writer.serialize(data)
            .map_err(|e| format!("Failed to write CSV record: {}", e))?;
    }
    
    writer.flush()
        .map_err(|e| format!("Failed to flush CSV writer: {}", e))?;
    
    println!("Parse Result Done! File Path: {}", output_path.display());
    Ok(())
}

// 扫描run文件夹
#[tauri::command]
async fn scan_run_folders(base_path: String) -> Result<ScanResult, String> {
    let path = Path::new(&base_path);
    if !path.exists() {
        return Err("路径不存在".to_string());
    }
    
    let run_regex = Regex::new(r"^run\d+$")
        .map_err(|e| format!("正则表达式错误: {}", e))?;
    
    let all_dirs = get_dirs(path)?;
    let mut run_folders = Vec::new();
    
    for dir_name in all_dirs {
        if run_regex.is_match(&dir_name) {
            let results_path = path.join(&dir_name).join("results");
            let has_results = results_path.exists();
            
            run_folders.push(RunFolderInfo {
                name: dir_name.clone(),
                has_results,
                status: if has_results { "已完成".to_string() } else { "未完成".to_string() },
            });
        }
    }
    
    // 按数字排序
    run_folders.sort_by(|a, b| {
        let a_num: i32 = a.name.replace("run", "").parse().unwrap_or(0);
        let b_num: i32 = b.name.replace("run", "").parse().unwrap_or(0);
        a_num.cmp(&b_num)
    });
    
    Ok(ScanResult {
        total: run_folders.len(),
        folders: run_folders,
    })
}

// 处理run文件夹
#[tauri::command]
async fn process_run_folders(base_path: String, selected_folders: Vec<String>) -> Result<String, String> {
    let base_path = Path::new(&base_path);
    if !base_path.exists() {
        return Err("基础路径不存在".to_string());
    }
    
    let mut all_data_list = Vec::new();
    let mut processed_count = 0;
    let mut log_messages = Vec::new();
    
    log_messages.push(format!("基础路径: {}", base_path.display()));
    log_messages.push(format!("选定的文件夹: {:?}", selected_folders));
    
    for run_folder in selected_folders {
        let run_num = run_folder.replace("run", "");
        log_messages.push(format!("\n处理 {} (run_num: {})", run_folder, run_num));
        
        let result_dir = base_path.join(&run_folder).join("results");
        let final_result_dir = base_path.join(&run_folder).join("final-result");
        
        if !result_dir.exists() {
            log_messages.push(format!("警告: {} 不存在，跳过 {}", result_dir.display(), run_folder));
            continue;
        }
        
        // 创建final-result目录
        if let Err(e) = fs::create_dir_all(&final_result_dir) {
            log_messages.push(format!("创建final-result目录失败: {}", e));
            continue;
        }
        
        match parse_result(&result_dir, &final_result_dir) {
            Ok(data_list) => {
                all_data_list.extend(data_list);
                processed_count += 1;
                log_messages.push(format!("成功处理 {}", run_folder));
            }
            Err(e) => {
                log_messages.push(format!("处理 {} 时出错: {}", run_folder, e));
            }
        }
    }
    
    if !all_data_list.is_empty() {
        if let Err(e) = write_result(&all_data_list, base_path) {
            log_messages.push(format!("写入最终结果失败: {}", e));
        } else {
            log_messages.push(format!("\n成功处理了 {} 个run文件夹", processed_count));
        }
    } else {
        log_messages.push("\n没有成功处理任何run文件夹".to_string());
    }
    
    Ok(log_messages.join("\n"))
}

// 文件重组
#[tauri::command]
async fn reorganize_files(
    source_dir: String, 
    output_dir: Option<String>, 
    merge_mode: String, 
    preserve_structure: bool
) -> Result<String, String> {
    let python_script = "../python_version/file_reorganizer.py";
    
    let mut cmd = Command::new("python3");
    cmd.arg(python_script).arg(&source_dir);
    
    if let Some(output) = output_dir {
        cmd.arg("--output").arg(output);
    }
    
    if merge_mode == "direct" {
        cmd.arg("--direct-merge");
    }
    
    if preserve_structure {
        cmd.arg("--preserve-structure");
    }
    
    let output = cmd.output()
        .map_err(|e| format!("执行失败: {}", e))?;
        
    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        return Err(format!("文件重组失败: {}", error));
    }
    
    Ok("文件重组完成".to_string())
}

// 图片尺寸调整
#[tauri::command]
async fn resize_images(
    files: Vec<String>,
    width: u32,
    height: u32,
    resize_mode: String,
    maintain_aspect_ratio: bool,
    quality: u32
) -> Result<String, String> {
    let python_script = "../python_version/image_resizer.py";
    
    for file in files {
        let mut cmd = Command::new("python3");
        cmd.arg(python_script)
           .arg(&file)
           .arg("--width").arg(width.to_string())
           .arg("--height").arg(height.to_string())
           .arg("--mode").arg(&resize_mode)
           .arg("--quality").arg(quality.to_string());
           
        if maintain_aspect_ratio {
            cmd.arg("--maintain-aspect");
        }
        
        let output = cmd.output()
            .map_err(|e| format!("执行失败: {}", e))?;
            
        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(format!("处理文件 {} 失败: {}", file, error));
        }
    }
    
    Ok("图片尺寸调整完成".to_string())
}

// PNG透明转黑色
#[tauri::command]
async fn convert_transparent_to_black(
    input_path: Option<String>,
    files: Option<Vec<String>>,
    output_path: Option<String>,
    recursive: bool
) -> Result<String, String> {
    let python_script = "../python_version/transparent_to_black.py";
    
    let mut cmd = Command::new("python3");
    cmd.arg(python_script);
    
    if let Some(path) = input_path {
        cmd.arg(&path);
    } else if let Some(file_list) = files {
        for file in file_list {
            cmd.arg(&file);
        }
    } else {
        return Err("必须提供输入路径或文件列表".to_string());
    }
    
    if let Some(output) = output_path {
        cmd.arg("-o").arg(output);
    }
    
    if recursive {
        cmd.arg("-r");
    }
    
    let output = cmd.output()
        .map_err(|e| format!("执行失败: {}", e))?;
        
    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        return Err(format!("PNG转换失败: {}", error));
    }
    
    Ok("PNG透明转黑色完成".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            process_binary_images,
            scan_run_folders,
            process_run_folders,
            reorganize_files,
            resize_images,
            convert_transparent_to_black
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
