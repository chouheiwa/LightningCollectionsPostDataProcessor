import React from 'react';
import { Layout as AntLayout, Menu, Typography } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  SwapOutlined,
  ToolOutlined,
  FolderOutlined,
  PictureOutlined,
  BgColorsOutlined
} from '@ant-design/icons';

const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/binary-inverter',
      icon: <SwapOutlined />,
      label: '二进制图像反转',
    },
    {
      key: '/post-process',
      icon: <ToolOutlined />,
      label: '后数据处理',
    },
    {
      key: '/file-reorganizer',
      icon: <FolderOutlined />,
      label: '文件重组',
    },
    {
      key: '/image-resizer',
      icon: <PictureOutlined />,
      label: '图片尺寸调整',
    },
    {
      key: '/transparent-to-black',
      icon: <BgColorsOutlined />,
      label: 'PNG透明转黑色',
    },
  ];

  const handleMenuClick = (key: string) => {
    navigate(key);
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider width={250} theme="light">
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
            数据处理工具
          </Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => handleMenuClick(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <AntLayout>
        <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 1px 4px rgba(0,21,41,.08)' }}>
          <Title level={3} style={{ margin: 0, lineHeight: '64px' }}>
            数据处理应用程序
          </Title>
        </Header>
        <Content style={{ margin: '24px', background: '#fff', padding: '24px', borderRadius: '8px' }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;