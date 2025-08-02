import React from 'react';
import { Card, Row, Col, Typography, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  SwapOutlined,
  ToolOutlined,
  FolderOutlined,
  PictureOutlined,
  BgColorsOutlined
} from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const navigate = useNavigate();

  const tools = [
    {
      key: 'binary-inverter',
      title: '二进制图像反转工具',
      description: '将二进制图像进行反转处理，黑白颜色互换',
      icon: <SwapOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      path: '/binary-inverter'
    },
    {
      key: 'post-process',
      title: '后数据处理工具',
      description: '对数据进行后期处理和分析',
      icon: <ToolOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      path: '/post-process'
    },
    {
      key: 'file-reorganizer',
      title: '文件重组工具',
      description: '重新组织和整理文件结构',
      icon: <FolderOutlined style={{ fontSize: '32px', color: '#faad14' }} />,
      path: '/file-reorganizer'
    },
    {
      key: 'image-resizer',
      title: '图片尺寸调整工具',
      description: '批量调整图片尺寸和分辨率',
      icon: <PictureOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      path: '/image-resizer'
    },
    {
      key: 'transparent-to-black',
      title: 'PNG透明转黑色工具',
      description: '将PNG图片的透明像素转换为黑色',
      icon: <BgColorsOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />,
      path: '/transparent-to-black'
    }
  ];

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <Title level={1}>数据处理工具集</Title>
        <Paragraph style={{ fontSize: '16px', color: '#666' }}>
          选择您需要使用的工具开始处理数据
        </Paragraph>
      </div>

      <Row gutter={[24, 24]}>
        {tools.map((tool) => (
          <Col xs={24} sm={12} lg={8} key={tool.key}>
            <Card
              hoverable
              style={{ height: '100%' }}
              styles={{ body: { textAlign: 'center', padding: '32px 24px' } }}
              onClick={() => navigate(tool.path)}
            >
              <div style={{ marginBottom: '16px' }}>
                {tool.icon}
              </div>
              <Title level={4} style={{ marginBottom: '12px' }}>
                {tool.title}
              </Title>
              <Paragraph style={{ color: '#666', marginBottom: '20px' }}>
                {tool.description}
              </Paragraph>
              <Button type="primary" size="large">
                开始使用
              </Button>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default Home;