import React, { useState } from 'react';
import { Card, Button, Input, message, Progress, Typography, Space, Divider, Radio, Checkbox } from 'antd';
import { FolderOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

const { Title, Paragraph } = Typography;

const FileReorganizer: React.FC = () => {
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [sourceDir, setSourceDir] = useState<string>('');
  const [outputDir, setOutputDir] = useState<string>('');
  const [mergeMode, setMergeMode] = useState<string>('direct');
  const [preserveStructure, setPreserveStructure] = useState<boolean>(false);

  const handleSelectSourceDir = async () => {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: '选择源目录'
      });
      
      if (selected) {
        setSourceDir(selected as string);
      }
    } catch (error) {
      message.error('选择目录失败: ' + error);
    }
  };

  const handleSelectOutputDir = async () => {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: '选择输出目录'
      });
      
      if (selected) {
        setOutputDir(selected as string);
      }
    } catch (error) {
      message.error('选择目录失败: ' + error);
    }
  };

  const handleProcess = async () => {
    if (!sourceDir) {
      message.warning('请先选择源目录');
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
      }, 400);

      // 调用 Tauri 命令重组文件
      const result = await invoke('reorganize_files', {
        sourceDir,
        outputDir: outputDir || undefined,
        mergeMode,
        preserveStructure
      });

      clearInterval(progressInterval);
      setProgress(100);
      
      message.success('文件重组完成！');
      console.log('处理结果:', result);
    } catch (error) {
      message.error('处理失败: ' + error);
      console.error('处理错误:', error);
    } finally {
      setProcessing(false);
      setTimeout(() => setProgress(0), 2000);
    }
  };

  return (
    <div>
      <Title level={2}>
        <FolderOutlined /> 文件重组工具
      </Title>
      <Paragraph>
        重新组织和整理文件结构，支持多种合并模式和目录结构保留选项。
      </Paragraph>

      <Divider />

      <Card title="目录选择" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Paragraph strong>源目录：</Paragraph>
            <Input.Group compact>
              <Input
                style={{ width: 'calc(100% - 120px)' }}
                placeholder="选择要重组的源目录"
                value={sourceDir}
                readOnly
              />
              <Button
                type="primary"
                icon={<FolderOpenOutlined />}
                onClick={handleSelectSourceDir}
              >
                选择目录
              </Button>
            </Input.Group>
          </div>

          <div>
            <Paragraph strong>输出目录（可选）：</Paragraph>
            <Input.Group compact>
              <Input
                style={{ width: 'calc(100% - 120px)' }}
                placeholder="选择输出目录（留空则在源目录处理）"
                value={outputDir}
                readOnly
              />
              <Button
                icon={<FolderOpenOutlined />}
                onClick={handleSelectOutputDir}
              >
                选择目录
              </Button>
            </Input.Group>
          </div>
        </Space>
      </Card>

      <Card title="重组选项" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Paragraph strong>合并模式：</Paragraph>
            <Radio.Group value={mergeMode} onChange={(e) => setMergeMode(e.target.value)}>
              <Space direction="vertical">
                <Radio value="direct">直接合并模式（推荐）</Radio>
                <Radio value="preserve">保留目录结构模式</Radio>
              </Space>
            </Radio.Group>
          </div>

          <div>
            <Checkbox
              checked={preserveStructure}
              onChange={(e) => setPreserveStructure(e.target.checked)}
            >
              保留原始目录结构
            </Checkbox>
          </div>

          {processing && (
            <div>
              <Paragraph>正在重组文件...</Paragraph>
              <Progress percent={progress} status={progress === 100 ? 'success' : 'active'} />
            </div>
          )}

          <Button
            type="primary"
            size="large"
            icon={<FolderOutlined />}
            loading={processing}
            onClick={handleProcess}
            disabled={!sourceDir}
          >
            {processing ? '重组中...' : '开始文件重组'}
          </Button>
        </Space>
      </Card>

      <Card title="使用说明">
        <ul>
          <li>选择需要重组的源目录</li>
          <li>可选择输出目录，留空则在源目录进行处理</li>
          <li><strong>直接合并模式：</strong>将所有文件移动到根目录，去除子目录结构</li>
          <li><strong>保留目录结构模式：</strong>保持原有的目录层次结构</li>
          <li>处理过程中会自动处理文件名冲突</li>
          <li>建议在处理前备份重要文件</li>
        </ul>
      </Card>
    </div>
  );
};

export default FileReorganizer;