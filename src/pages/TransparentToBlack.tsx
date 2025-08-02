import React, { useState } from 'react';
import { Card, Button, Upload, message, Progress, Typography, Space, Divider, Checkbox, Input } from 'antd';
import { InboxOutlined, BgColorsOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

const { Title, Paragraph } = Typography;
const { Dragger } = Upload;

const TransparentToBlack: React.FC = () => {
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fileList, setFileList] = useState<any[]>([]);
  const [inputPath, setInputPath] = useState<string>('');
  const [outputPath, setOutputPath] = useState<string>('');
  const [recursive, setRecursive] = useState<boolean>(false);
  const [useFolder, setUseFolder] = useState<boolean>(false);

  const handleSelectInputPath = async () => {
    try {
      const selected = await open({
        directory: useFolder,
        multiple: false,
        title: useFolder ? '选择输入文件夹' : '选择PNG文件',
        filters: useFolder ? undefined : [
          {
            name: 'PNG Images',
            extensions: ['png']
          }
        ]
      });
      
      if (selected) {
        setInputPath(selected as string);
      }
    } catch (error) {
      message.error('选择路径失败: ' + error);
    }
  };

  const handleSelectOutputPath = async () => {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: '选择输出文件夹'
      });
      
      if (selected) {
        setOutputPath(selected as string);
      }
    } catch (error) {
      message.error('选择路径失败: ' + error);
    }
  };

  const handleProcess = async () => {
    if (!useFolder && fileList.length === 0) {
      message.warning('请先选择要处理的PNG文件');
      return;
    }

    if (useFolder && !inputPath) {
      message.warning('请先选择输入路径');
      return;
    }

    setProcessing(true);
    setProgress(0);

    try {
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 12;
        });
      }, 250);

      // 调用 Tauri 命令处理PNG透明像素
      const result = await invoke('convert_transparent_to_black', {
        inputPath: useFolder ? inputPath : undefined,
        files: useFolder ? undefined : fileList.map(file => file.originFileObj?.path || file.name),
        outputPath: outputPath || undefined,
        recursive
      });

      clearInterval(progressInterval);
      setProgress(100);
      
      message.success('PNG透明像素转换完成！');
      console.log('处理结果:', result);
    } catch (error) {
      message.error('处理失败: ' + error);
      console.error('处理错误:', error);
    } finally {
      setProcessing(false);
      setTimeout(() => setProgress(0), 2000);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: true,
    accept: '.png',
    fileList,
    beforeUpload: () => false,
    onChange: (info: any) => {
      setFileList(info.fileList);
    },
    onDrop: (e: any) => {
      console.log('拖拽文件:', e.dataTransfer.files);
    },
  };

  return (
    <div>
      <Title level={2}>
        <BgColorsOutlined /> PNG透明像素转黑色工具
      </Title>
      <Paragraph>
        将PNG图片的透明像素转换为黑色像素。支持单文件处理和批量文件夹处理。
      </Paragraph>

      <Divider />

      <Card title="输入方式选择" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Checkbox
            checked={useFolder}
            onChange={(e) => setUseFolder(e.target.checked)}
          >
            使用文件夹批量处理（而非单独选择文件）
          </Checkbox>

          {useFolder ? (
            <div>
              <Paragraph strong>输入路径：</Paragraph>
              <Input.Group compact>
                <Input
                  style={{ width: 'calc(100% - 120px)' }}
                  placeholder="选择包含PNG文件的文件夹"
                  value={inputPath}
                  readOnly
                />
                <Button
                  type="primary"
                  icon={<FolderOpenOutlined />}
                  onClick={handleSelectInputPath}
                >
                  选择文件夹
                </Button>
              </Input.Group>
            </div>
          ) : (
            <div>
              <Dragger {...uploadProps}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽PNG文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持单个或批量上传PNG文件
                </p>
              </Dragger>

              {fileList.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <Paragraph strong>已选择 {fileList.length} 个PNG文件</Paragraph>
                </div>
              )}
            </div>
          )}
        </Space>
      </Card>

      <Card title="输出设置" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Paragraph strong>输出路径（可选）：</Paragraph>
            <Input.Group compact>
              <Input
                style={{ width: 'calc(100% - 120px)' }}
                placeholder="选择输出文件夹（留空则在原位置保存）"
                value={outputPath}
                readOnly
              />
              <Button
                icon={<FolderOpenOutlined />}
                onClick={handleSelectOutputPath}
              >
                选择文件夹
              </Button>
            </Input.Group>
          </div>

          {useFolder && (
            <div>
              <Checkbox
                checked={recursive}
                onChange={(e) => setRecursive(e.target.checked)}
              >
                递归处理子文件夹
              </Checkbox>
            </div>
          )}
        </Space>
      </Card>

      <Card title="开始处理" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {processing && (
            <div>
              <Paragraph>正在转换PNG透明像素...</Paragraph>
              <Progress percent={progress} status={progress === 100 ? 'success' : 'active'} />
            </div>
          )}

          <Button
            type="primary"
            size="large"
            icon={<BgColorsOutlined />}
            loading={processing}
            onClick={handleProcess}
            disabled={useFolder ? !inputPath : fileList.length === 0}
          >
            {processing ? '处理中...' : '开始转换'}
          </Button>
        </Space>
      </Card>

      <Card title="使用说明">
        <ul>
          <li>选择需要处理的PNG文件或包含PNG文件的文件夹</li>
          <li>可选择输出路径，留空则在原文件位置保存</li>
          <li>文件夹模式支持递归处理子文件夹中的PNG文件</li>
          <li>处理后的文件将保存为新文件，原文件不会被覆盖</li>
          <li>透明像素（Alpha通道为0）将被转换为黑色像素</li>
          <li>半透明像素将根据透明度与黑色混合</li>
          <li>处理后的文件名会添加 "_no_transparent" 后缀</li>
        </ul>
      </Card>
    </div>
  );
};

export default TransparentToBlack;