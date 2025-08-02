import React, { useState, useEffect } from 'react';
import { Card, Button, Progress, message, Typography, Space, Alert, Table, Input, Tag } from 'antd';
import { FolderOpenOutlined, PlayCircleOutlined, FileTextOutlined, ReloadOutlined, CheckSquareOutlined, BorderOutlined } from '@ant-design/icons';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

const { Title, Text } = Typography;

interface RunFolder {
  key: string;
  folder: string;
  status: 'pending' | 'processing' | 'completed' | 'error' | 'skipped';
  resultsExist: boolean;
  selected: boolean;
}

interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

const PostDataProcess: React.FC = () => {
  const [basePath, setBasePath] = useState<string>('/Users/chouheiwa/Downloads/data_results_current');
  const [runFolders, setRunFolders] = useState<RunFolder[]>([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [statusText, setStatusText] = useState('准备就绪');

  const addLog = (message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  const selectBasePath = async () => {
    try {
      const selected = await open({
        directory: true,
        defaultPath: basePath,
      });
      
      if (selected) {
        setBasePath(selected as string);
        refreshRunFolders(selected as string);
      }
    } catch (error) {
      message.error('选择路径失败');
    }
  };

  const refreshRunFolders = async (path?: string) => {
    const targetPath = path || basePath;
    try {
      setStatusText('正在刷新...');
      
      const result = await invoke('scan_run_folders', {
        basePath: targetPath
      });

      console.log('扫描结果:', result);
      
      let folders: RunFolder[] = [];
      if (result && typeof result === 'object' && 'folders' in result) {
        folders = (result.folders as any[]).map((folder, index) => ({
          key: index.toString(),
          folder: folder.name,
          status: 'pending' as const,
          resultsExist: folder.hasResults,
          selected: false,
        }));
      }

      setRunFolders(folders);
      setStatusText(`找到 ${folders.length} 个run文件夹`);
      addLog(`刷新完成，找到 ${folders.length} 个run文件夹: ${folders.map(f => f.folder).join(', ')}`);
    } catch (error) {
      setStatusText('刷新失败');
      addLog(`刷新失败: ${error}`, 'error');
      message.error('刷新失败');
    }
  };

  const toggleSelection = (key: string) => {
    setRunFolders(prev => prev.map(folder => 
      folder.key === key ? { ...folder, selected: !folder.selected } : folder
    ));
  };

  const selectAll = () => {
    setRunFolders(prev => prev.map(folder => ({ ...folder, selected: true })));
  };

  const deselectAll = () => {
    setRunFolders(prev => prev.map(folder => ({ ...folder, selected: false })));
  };

  const startProcessing = async () => {
    const selectedFolders = runFolders.filter(f => f.selected);
    
    if (selectedFolders.length === 0) {
      message.warning('请选择要处理的run文件夹');
      return;
    }

    setProcessing(true);
    setProgress(0);
    addLog(`开始处理 ${selectedFolders.length} 个run文件夹...`);

    try {
      const selectedFolderNames = selectedFolders.map(f => f.folder);
      
      // 更新状态为处理中
      setRunFolders(prev => prev.map(folder => 
        folder.selected ? { ...folder, status: 'processing' as const } : folder
      ));

      const result = await invoke('process_run_folders', {
        basePath,
        selectedFolders: selectedFolderNames
      });

      // 处理结果日志
      const logOutput = result as string;
      const logLines = logOutput.split('\n');
      
      // 添加处理日志
      logLines.forEach(line => {
        if (line.trim()) {
          if (line.includes('成功处理')) {
            addLog(line, 'success');
          } else if (line.includes('错误') || line.includes('失败')) {
            addLog(line, 'error');
          } else {
            addLog(line);
          }
        }
      });

      // 更新所有选中文件夹的状态为完成
      setRunFolders(prev => prev.map(folder => 
        folder.selected ? { ...folder, status: 'completed' as const } : folder
      ));

      setProgress(100);
      addLog('所有选定的run文件夹处理完成!', 'success');
      message.success('数据处理完成！');
    } catch (error) {
      // 更新选中文件夹的状态为错误
      setRunFolders(prev => prev.map(folder => 
        folder.selected ? { ...folder, status: 'error' as const } : folder
      ));
      
      addLog(`处理过程中发生错误: ${error}`, 'error');
      message.error(`处理失败: ${error}`);
    } finally {
      setProcessing(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  useEffect(() => {
    refreshRunFolders();
  }, []);

  const columns = [
    {
      title: '选择',
      key: 'select',
      width: 60,
      render: (_: any, record: RunFolder) => (
        <Button
          type="text"
          icon={record.selected ? <CheckSquareOutlined /> : <BorderOutlined />}
          onClick={() => toggleSelection(record.key)}
        />
      ),
    },
    {
      title: 'Run文件夹',
      dataIndex: 'folder',
      key: 'folder',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap = {
          pending: { color: 'default', text: '待处理' },
          processing: { color: 'processing', text: '处理中...' },
          completed: { color: 'success', text: '完成' },
          error: { color: 'error', text: '错误' },
          skipped: { color: 'warning', text: '跳过' },
        };
        const config = statusMap[status as keyof typeof statusMap];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: 'Results目录',
      dataIndex: 'resultsExist',
      key: 'resultsExist',
      render: (exists: boolean) => (
        <Text type={exists ? 'success' : 'danger'}>
          {exists ? '✓' : '✗'}
        </Text>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <FileTextOutlined /> 后数据处理工具
      </Title>
      
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message="功能说明"
          description="扫描指定目录下的run文件夹，处理其中的机器学习实验结果数据，生成汇总的CSV文件。"
          type="info"
          showIcon
        />

        <Card title="路径设置" size="small">
          <Space style={{ width: '100%' }}>
            <Text strong>基础路径：</Text>
            <Input
              value={basePath}
              onChange={(e) => setBasePath(e.target.value)}
              style={{ flex: 1, maxWidth: 400 }}
              placeholder="请输入或选择基础路径"
            />
            <Button icon={<FolderOpenOutlined />} onClick={selectBasePath}>
              浏览
            </Button>
            <Button icon={<ReloadOutlined />} onClick={() => refreshRunFolders()}>
              刷新
            </Button>
          </Space>
        </Card>

        <Card 
          title={`Run文件夹列表 - ${statusText}`}
          size="small"
          extra={
            <Space>
              <Button size="small" onClick={selectAll}>全选</Button>
              <Button size="small" onClick={deselectAll}>取消全选</Button>
            </Space>
          }
        >
          <Table
            columns={columns}
            dataSource={runFolders}
            pagination={false}
            size="small"
            scroll={{ y: 300 }}
          />
        </Card>

        <Card title="处理控制" size="small">
          <Space style={{ width: '100%' }}>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={startProcessing}
              loading={processing}
              disabled={runFolders.filter(f => f.selected).length === 0}
            >
              {processing ? '处理中...' : '开始处理'}
            </Button>
            
            {processing && (
              <div style={{ flex: 1, marginLeft: 16 }}>
                <Progress percent={progress} status="active" />
              </div>
            )}
          </Space>
        </Card>

        <Card 
          title="处理日志" 
          size="small"
          extra={<Button size="small" onClick={clearLogs}>清除日志</Button>}
        >
          <div style={{ height: 200, overflow: 'auto', backgroundColor: '#fafafa', padding: 8, borderRadius: 4 }}>
            {logs.map((log, index) => (
              <div key={index} style={{ marginBottom: 4, fontSize: 12 }}>
                <Text type="secondary">[{log.timestamp}]</Text>
                <Text type={log.type === 'error' ? 'danger' : log.type === 'success' ? 'success' : 'secondary'} style={{ marginLeft: 8 }}>
                  {log.message}
                </Text>
              </div>
            ))}
          </div>
        </Card>
      </Space>
    </div>
  );
};

export default PostDataProcess;