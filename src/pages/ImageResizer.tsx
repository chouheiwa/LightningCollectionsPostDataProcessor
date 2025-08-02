import React, { useState } from 'react';
import { Card, Button, Upload, message, Progress, Typography, Space, Divider, InputNumber, Row, Col, Select, Checkbox } from 'antd';
import { InboxOutlined, PictureOutlined } from '@ant-design/icons';
import { invoke } from '@tauri-apps/api/core';

const { Title, Paragraph } = Typography;
const { Dragger } = Upload;
const { Option } = Select;

const ImageResizer: React.FC = () => {
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fileList, setFileList] = useState<any[]>([]);
  const [width, setWidth] = useState<number>(800);
  const [height, setHeight] = useState<number>(600);
  const [resizeMode, setResizeMode] = useState<string>('exact');
  const [maintainAspectRatio, setMaintainAspectRatio] = useState<boolean>(true);
  const [quality, setQuality] = useState<number>(90);

  const resizeModes = [
    { value: 'exact', label: '精确尺寸' },
    { value: 'fit', label: '适应尺寸（保持比例）' },
    { value: 'fill', label: '填充尺寸（可能裁剪）' },
    { value: 'stretch', label: '拉伸填充' }
  ];

  const handleProcess = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择要处理的图片文件');
      return;
    }

    if (!width || !height || width <= 0 || height <= 0) {
      message.warning('请输入有效的宽度和高度');
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
      }, 300);

      // 调用 Tauri 命令调整图片尺寸
      const result = await invoke('resize_images', {
        files: fileList.map(file => file.originFileObj?.path || file.name),
        width,
        height,
        resizeMode,
        maintainAspectRatio,
        quality
      });

      clearInterval(progressInterval);
      setProgress(100);
      
      message.success('图片尺寸调整完成！');
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
    accept: '.png,.jpg,.jpeg,.bmp,.tiff,.webp',
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
        <PictureOutlined /> 图片尺寸调整工具
      </Title>
      <Paragraph>
        批量调整图片尺寸和分辨率。支持多种调整模式和质量设置。
      </Paragraph>

      <Divider />

      <Card title="选择图片文件" style={{ marginBottom: '24px' }}>
        <Dragger {...uploadProps} style={{ marginBottom: '16px' }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个或批量上传。支持 PNG、JPG、JPEG、BMP、TIFF、WebP 格式
          </p>
        </Dragger>

        {fileList.length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <Paragraph strong>已选择 {fileList.length} 个文件</Paragraph>
          </div>
        )}
      </Card>

      <Card title="尺寸设置" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Row gutter={16}>
            <Col span={8}>
              <Paragraph strong>宽度 (px)：</Paragraph>
              <InputNumber
                style={{ width: '100%' }}
                min={1}
                max={10000}
                value={width}
                onChange={(value) => setWidth(value || 800)}
                placeholder="输入宽度"
              />
            </Col>
            <Col span={8}>
              <Paragraph strong>高度 (px)：</Paragraph>
              <InputNumber
                style={{ width: '100%' }}
                min={1}
                max={10000}
                value={height}
                onChange={(value) => setHeight(value || 600)}
                placeholder="输入高度"
              />
            </Col>
            <Col span={8}>
              <Paragraph strong>质量 (%)：</Paragraph>
              <InputNumber
                style={{ width: '100%' }}
                min={1}
                max={100}
                value={quality}
                onChange={(value) => setQuality(value || 90)}
                placeholder="输入质量"
              />
            </Col>
          </Row>

          <div>
            <Paragraph strong>调整模式：</Paragraph>
            <Select
              style={{ width: '300px' }}
              value={resizeMode}
              onChange={setResizeMode}
              placeholder="选择调整模式"
            >
              {resizeModes.map(mode => (
                <Option key={mode.value} value={mode.value}>
                  {mode.label}
                </Option>
              ))}
            </Select>
          </div>

          <div>
            <Checkbox
              checked={maintainAspectRatio}
              onChange={(e) => setMaintainAspectRatio(e.target.checked)}
            >
              保持宽高比
            </Checkbox>
          </div>
        </Space>
      </Card>

      <Card title="开始处理" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {processing && (
            <div>
              <Paragraph>正在调整图片尺寸...</Paragraph>
              <Progress percent={progress} status={progress === 100 ? 'success' : 'active'} />
            </div>
          )}

          <Button
            type="primary"
            size="large"
            icon={<PictureOutlined />}
            loading={processing}
            onClick={handleProcess}
            disabled={fileList.length === 0}
          >
            {processing ? '处理中...' : '开始调整尺寸'}
          </Button>
        </Space>
      </Card>

      <Card title="使用说明">
        <ul>
          <li>选择需要调整尺寸的图片文件</li>
          <li>设置目标宽度和高度（像素）</li>
          <li>选择合适的调整模式：
            <ul>
              <li><strong>精确尺寸：</strong>严格按照指定尺寸调整</li>
              <li><strong>适应尺寸：</strong>在指定尺寸内保持原始比例</li>
              <li><strong>填充尺寸：</strong>填满指定尺寸，可能会裁剪</li>
              <li><strong>拉伸填充：</strong>拉伸图片以填满指定尺寸</li>
            </ul>
          </li>
          <li>调整质量参数（仅对 JPEG 格式有效）</li>
          <li>处理后的图片将保存在原文件同目录下，文件名添加尺寸后缀</li>
        </ul>
      </Card>
    </div>
  );
};

export default ImageResizer;