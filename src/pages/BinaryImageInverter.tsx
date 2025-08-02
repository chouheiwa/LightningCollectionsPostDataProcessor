import React, { useState } from 'react';
import { Card, Button, Upload, message, Progress, Typography, Space, Divider } from 'antd';
import { InboxOutlined, SwapOutlined } from '@ant-design/icons';
import { invoke } from '@tauri-apps/api/core';

const { Title, Paragraph } = Typography;
const { Dragger } = Upload;

const BinaryImageInverter: React.FC = () => {
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fileList, setFileList] = useState<any[]>([]);

  const handleProcess = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择要处理的图像文件');
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
          return prev + 10;
        });
      }, 200);

      // 调用 Tauri 命令处理图像
      const result = await invoke('process_binary_images', {
        files: fileList.map(file => file.originFileObj?.path || file.name)
      });

      clearInterval(progressInterval);
      setProgress(100);
      
      message.success('图像反转处理完成！');
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
    accept: '.png,.jpg,.jpeg,.bmp,.tiff',
    fileList,
    beforeUpload: () => false, // 阻止自动上传
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
        <SwapOutlined /> 二进制图像反转工具
      </Title>
      <Paragraph>
        将二进制图像进行反转处理，黑白颜色互换。支持 PNG、JPG、JPEG、BMP、TIFF 格式。
      </Paragraph>

      <Divider />

      <Card title="选择图像文件" style={{ marginBottom: '24px' }}>
        <Dragger {...uploadProps} style={{ marginBottom: '16px' }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个或批量上传。支持 PNG、JPG、JPEG、BMP、TIFF 格式
          </p>
        </Dragger>

        {fileList.length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <Paragraph strong>已选择 {fileList.length} 个文件</Paragraph>
          </div>
        )}
      </Card>

      <Card title="处理选项">
        <Space direction="vertical" style={{ width: '100%' }}>
          {processing && (
            <div>
              <Paragraph>正在处理图像...</Paragraph>
              <Progress percent={progress} status={progress === 100 ? 'success' : 'active'} />
            </div>
          )}

          <Button
            type="primary"
            size="large"
            icon={<SwapOutlined />}
            loading={processing}
            onClick={handleProcess}
            disabled={fileList.length === 0}
          >
            {processing ? '处理中...' : '开始反转处理'}
          </Button>
        </Space>
      </Card>

      <Card title="使用说明" style={{ marginTop: '24px' }}>
        <ul>
          <li>选择需要处理的二进制图像文件</li>
          <li>支持批量处理多个文件</li>
          <li>处理后的图像将保存在原文件同目录下，文件名添加 "_inverted" 后缀</li>
          <li>黑色像素将变为白色，白色像素将变为黑色</li>
        </ul>
      </Card>
    </div>
  );
};

export default BinaryImageInverter;