# B站视频下载器 (Bilibili Video Downloader)

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/BiliDownloader)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/BiliDownloader.svg?style=social)](https://github.com/yourusername/BiliDownloader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/BiliDownloader.svg?style=social)](https://github.com/yourusername/BiliDownloader/network/members)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/BiliDownloader.svg)](https://github.com/yourusername/BiliDownloader/issues)

一个功能强大的B站视频下载工具，支持命令行和图形界面两种使用方式。

## 🎯 功能特点

### 核心功能
- **多种下载模式**：支持视频、音频、封面图片单独或组合下载
- **多清晰度选择**：支持从360P到4K多种视频质量
- **智能合并**：自动合并视频和音频流（需要ffmpeg）
- **扫码登录**：支持登录获取高清视频内容
- **批量下载**：支持连续下载多个视频

### 🖥️ 使用方式
- **命令行版本**：`BiliDownloader.py` - 适合高级用户和批量操作
- **图形界面版本**：`BiliDownloader_GUI.py` - 用户友好，可视化操作

### 📁 输出格式
- 视频：MP4格式
- 音频：M4A格式  
- 封面：JPG格式

## 📦 安装说明

### 系统要求
- Python 3.7 或更高版本
- Windows / macOS / Linux

### 安装依赖
```bash
# 使用 pip 安装
pip install requests pyqt5 qrcode pillow

# 或者使用 requirements.txt
pip install -r requirements.txt
```

### 可选依赖（用于视频合并）
```bash
# 需要安装ffmpeg
# Windows: 下载ffmpeg并添加到PATH
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

## 🚀 快速开始

### 图形界面版本（推荐）
```bash
python BiliDownloader_GUI.py
```

**界面功能区域：**
1. **基本设置**：输入BV号/URL，设置下载目录
2. **下载选项**：选择下载类型、视频质量、高级选项
3. **进度输出**：实时显示下载进度和日志信息

**操作步骤：**
1. 在主界面输入B站视频的BV号或完整URL
2. 点击"扫码登录"获取高清视频（可选）
3. 在"下载选项"标签页选择下载类型和质量
4. 点击"开始下载"

### 命令行版本
```bash
python BiliDownloader.py
```

## 🔧 高级用法

### 批量下载
支持通过文件批量下载：
```bash
# 创建包含视频URL的文本文件
echo "https://www.bilibili.com/video/BV1xxx" >> videos.txt
echo "https://www.bilibili.com/video/BV2xxx" >> videos.txt

# 使用脚本批量处理
python batch_download.py -f videos.txt
```

### API 集成
可以作为模块集成到其他项目中：
```python
from BiliDownloader import BilibiliDownloader

downloader = BilibiliDownloader()
downloader.download_video("BV1xxx", quality=80, download_type="video+audio")
```

## 📊 下载类型说明

| 类型 | 说明 | 输出文件 |
|------|------|----------|
| 仅视频 | 下载视频流（无音频） | .mp4 |
| 仅音频 | 下载音频流 | .m4a |
| 视频+音频 | 分别下载后自动合并 | .mp4 |
| 仅封面图片 | 下载视频封面 | .jpg |
| 视频+音频+封面 | 完整下载所有内容 | 多个文件 |

## 🎬 视频质量对照表

| 代码 | 分辨率 | 说明 | 是否需要登录 |
|------|--------|------|-------------|
| 120 | 4K | 超清 | 是 |
| 116 | 1080P | 60帧 | 是 |
| 112 | 1080P+ | 高码率 | 是 |
| 80 | 1080P | 高清 | 是 |
| 64 | 720P | 高清 | 否 |
| 32 | 480P | 清晰 | 否 |
| 16 | 360P | 流畅 | 否 |

## ⚠️ 注意事项

### 重要提醒
1. **版权保护**：请仅下载个人观看的视频，尊重内容创作者版权
2. **登录限制**：部分高清视频需要登录后才能下载
3. **ffmpeg依赖**：视频音频合并功能需要系统安装ffmpeg
4. **网络要求**：下载速度取决于网络环境和B站服务器状态

### 🔧 常见问题

**Q: 下载失败怎么办？**
A: 
- 检查网络连接
- 确认视频URL正确
- 尝试重新登录
- 查看控制台错误信息

**Q: 合并视频失败？**  
A: 
- 确认系统已安装ffmpeg
- 检查ffmpeg是否在PATH环境变量中
- 或手动合并下载的视频和音频文件

**Q: 无法获取高清视频？**
A: 需要扫码登录B站账号，部分视频需要大会员权限

**Q: 文件名乱码？**
A: 程序会自动过滤非法字符，确保文件名兼容各操作系统

## 📁 项目结构
```
BiliDownloader/
├── BiliDownloader.py          # 核心下载模块
├── BiliDownloader_GUI.py      # 图形界面模块
├── requirements.txt           # 依赖包列表
├── LICENSE                    # 许可证文件
├── README.md                  # 说明文档
└── examples/                  # 使用示例
    ├── batch_download.py      # 批量下载脚本
    └── api_usage.py           # API使用示例
```

## 🔧 技术特性
- 多线程下载，支持进度显示
- 自动重试机制，提升下载成功率  
- 智能文件名处理，避免特殊字符问题
- 模块化设计，易于维护和扩展
- 完整的错误处理和日志记录

## 🛠️ 开发

### 贡献指南
欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

### 开发环境设置
```bash
git clone https://github.com/yourusername/BiliDownloader.git
cd BiliDownloader
pip install -r requirements.txt
```

## 📄 许可证
本项目采用 MIT 许可证 - 详见 [LICENSE](https://github.com/yanodaPro/Miscellaneous/blob/main/BiliDownloader/LICENSE) 文件

## ⚖️ 免责声明
本工具仅供学习和个人使用，请遵守相关法律法规和B站用户协议。不得将下载内容用于商业用途或侵犯版权的行为。使用本工具产生的任何问题由使用者自行承担。
