# Miscellaneous Utilities Collection

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yanodaPro/Miscellaneous)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/yanodaPro/Miscellaneous/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/yanodaPro/Miscellaneous.svg?style=social)](https://github.com/yanodaPro/Miscellaneous/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yanodaPro/Miscellaneous.svg?style=social)](https://github.com/yanodaPro/Miscellaneous/network/members)
[![GitHub issues](https://img.shields.io/github/issues/yanodaPro/Miscellaneous.svg)](https://github.com/yanodaPro/Miscellaneous/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/yanodaPro/Miscellaneous.svg)](https://github.com/yanodaPro/Miscellaneous/commits/main)

一个实用的工具集合仓库，包含多种日常使用的实用程序。

## 📦 项目概览

```
Miscellaneous-main/
├── BiliDownloader/          # B站视频下载工具
└── file_time_changer/       # 文件时间修改工具
```

## 🎯 工具列表

### 1. B站视频下载器 (Bilibili Video Downloader)

一个功能强大的B站视频下载工具，支持命令行和图形界面两种使用方式。

**主要功能：**
- 多种下载模式：视频、音频、封面图片单独或组合下载
- 多清晰度选择：支持从360P到4K多种视频质量
- 智能合并：自动合并视频和音频流
- 扫码登录：支持登录获取高清视频内容
- 批量下载：支持连续下载多个视频

**快速开始：**
```bash
cd BiliDownloader
pip install -r requirements.txt
python BiliDownloader_GUI.py  # 图形界面版本
# 或
python BiliDownloader.py      # 命令行版本
```

[查看详细文档](./BiliDownloader/README.md)

### 2. 文件时间修改器 (File Time Changer)

一个用于修改Windows文件和目录时间戳的实用工具。

**主要功能：**
- 修改创建时间、修改时间和访问时间
- 支持文件和目录操作
- 简单易用的命令行界面

**快速开始：**
```bash
cd file_time_changer
python file_time_changer.py "文件或目录路径" [选项]
```

[查看详细文档](./file_time_changer/README.md)

## 🚀 快速导航

| 工具 | 类型 | 主要用途 | 使用难度 |
|------|------|----------|----------|
| [BiliDownloader](./BiliDownloader/) | 多媒体工具 | B站视频下载 | 初学者 |
| [File Time Changer](./file_time_changer/) | 系统工具 | 文件时间管理 | 中级 |

## 📋 系统要求

- **操作系统**: Windows / macOS / Linux
- **Python**: 3.7 或更高版本
- **依赖管理**: pip

## 🔧 安装与配置

### 克隆仓库
```bash
git clone https://github.com/yanodaPro/Miscellaneous.git
cd Miscellaneous
```

### 安装依赖
每个工具都有独立的依赖要求，请进入相应目录查看具体说明：

```bash
# 或者使用单个命令安装所有依赖
pip install PyQt5 requests qrcode pillow pywin32 ffmpeg-python python-dateutil
```
如果你使用的是较新的Python版本，也可以使用以下更简洁的命令：
```bash
pip install PyQt5 requests qrcode[pil] pywin32 ffmpeg-python python-dateutil
```

## 🛠️ 开发与贡献

欢迎为这个项目贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/新功能`
3. 提交更改：`git commit -m '添加新功能'`
4. 推送分支：`git push origin feature/新功能`
5. 提交 Pull Request

### 开发环境设置
```bash
git clone https://github.com/yanodaPro/Miscellaneous.git
cd Miscellaneous
# 根据具体工具安装对应依赖
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](./LICENSE) 文件。

## ⚖️ 免责声明

本仓库中的工具仅供学习和个人使用，请遵守相关法律法规和平台用户协议。不得将工具用于商业用途或侵犯版权的行为。使用本工具产生的任何问题由使用者自行承担。

## 🤝 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/yanodaPro/Miscellaneous/issues)
- 查看详细文档和常见问题解答
- 参与社区讨论

---

**注意**: 每个工具都有独立的文档和使用说明，请在使用前仔细阅读相应目录下的README文件。
```
