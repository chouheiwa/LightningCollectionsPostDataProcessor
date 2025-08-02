import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Layout from './components/Layout';
import Home from './pages/Home';
import BinaryImageInverter from './pages/BinaryImageInverter';
import PostDataProcess from './pages/PostDataProcess';
import FileReorganizer from './pages/FileReorganizer';
import ImageResizer from './pages/ImageResizer';
import TransparentToBlack from './pages/TransparentToBlack';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/binary-inverter" element={<BinaryImageInverter />} />
            <Route path="/post-process" element={<PostDataProcess />} />
            <Route path="/file-reorganizer" element={<FileReorganizer />} />
            <Route path="/image-resizer" element={<ImageResizer />} />
            <Route path="/transparent-to-black" element={<TransparentToBlack />} />
          </Routes>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;
