import sys
import os
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QTabWidget, QHeaderView, QTextEdit,
                             QDoubleSpinBox, QSpinBox, QComboBox, QMessageBox, QCheckBox,
                             QFileDialog, QProgressBar, QListWidget, QListWidgetItem, QRadioButton,
                             QButtonGroup)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor

# 导入B站下载器类
from BiliDownloader import BilibiliVideoDownloader


class DownloadWorker(QThread):
    """下载工作线程"""
    progress_signal = pyqtSignal(str, int)  # 文件名, 进度百分比
    log_signal = pyqtSignal(str)  # 日志消息
    finished_signal = pyqtSignal(bool, str)  # 成功状态, 消息
    file_progress_signal = pyqtSignal(str, int, int)  # 文件名, 已下载大小, 总大小

    def __init__(self, downloader, input_str, quality, download_type, download_path):
        super().__init__()
        self.downloader = downloader
        self.input_str = input_str
        self.quality = quality
        self.download_type = download_type
        self.download_path = download_path
        self.is_running = True

    def run(self):
        try:
            # 保存原始工作目录
            original_dir = os.getcwd()

            # 切换到下载目录
            if self.download_path:
                os.chdir(self.download_path)

            self.log_signal.emit(f"开始下载: {self.input_str}")
            self.log_signal.emit(f"下载类型: {self.get_download_type_name()}")
            self.log_signal.emit(f"下载目录: {os.getcwd()}")

            # 执行下载
            success = self.downloader.download_video_by_bvid(
                self.input_str,
                self.quality,
                self.download_type
            )

            # 恢复原始目录
            os.chdir(original_dir)

            if success:
                self.finished_signal.emit(True, "下载完成!")
            else:
                self.finished_signal.emit(False, "下载失败!")

        except Exception as e:
            self.finished_signal.emit(False, f"下载过程中出错: {str(e)}")

    def get_download_type_name(self):
        """获取下载类型名称"""
        type_map = {
            '1': '仅视频',
            '2': '仅音频',
            '3': '视频+音频',
            '4': '仅封面',
            '5': '视频+音频+封面'
        }
        return type_map.get(self.download_type, '未知类型')


class BiliDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.downloader = BilibiliVideoDownloader()
        self.download_thread = None
        self.current_file = ""
        self.init_ui()
        self.update_login_status()

    def init_ui(self):
        self.setWindowTitle("B站视频下载器 GUI")
        self.setGeometry(100, 100, 1000, 700)

        # 设置极简风格
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1a252f;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
                padding: 8px;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
        """)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("B站视频下载器 (支持Cookie保存)")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
            }
        """)
        main_layout.addWidget(title_label)

        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 基本设置页
        self.basic_tab = self.create_basic_tab()
        self.tabs.addTab(self.basic_tab, "基本设置")

        # 下载选项页
        self.options_tab = self.create_options_tab()
        self.tabs.addTab(self.options_tab, "下载选项")

        # 进度输出页
        self.output_tab = self.create_output_tab()
        self.tabs.addTab(self.output_tab, "进度输出")

        # 按钮区域
        button_layout = QHBoxLayout()

        self.login_btn = QPushButton("扫码登录")
        self.login_btn.clicked.connect(self.login_bilibili)

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.clicked.connect(self.logout_bilibili)

        self.download_btn = QPushButton("开始下载")
        self.download_btn.clicked.connect(self.start_download)

        self.clear_btn = QPushButton("清除设置")
        self.clear_btn.clicked.connect(self.clear_settings)

        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.logout_btn)
        button_layout.addWidget(self.download_btn)

        main_layout.addLayout(button_layout)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.statusBar().addWidget(self.status_label)

    def create_basic_tab(self):
        """创建基本设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 视频输入组
        input_group = QGroupBox("视频信息")
        input_layout = QVBoxLayout()

        # BV号/URL输入
        url_row = QHBoxLayout()
        url_row.addWidget(QLabel("BV号或URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入BV号或视频URL，例如: BV1xx411c7mh")
        url_row.addWidget(self.url_input)
        input_layout.addLayout(url_row)

        # 登录状态
        login_row = QHBoxLayout()
        login_row.addWidget(QLabel("登录状态:"))
        self.login_status = QLabel("未登录")
        self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        login_row.addWidget(self.login_status)
        login_row.addStretch()
        input_layout.addLayout(login_row)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 下载路径组
        path_group = QGroupBox("下载设置")
        path_layout = QVBoxLayout()

        # 下载目录选择
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("下载目录:"))
        self.download_dir = QLineEdit()
        self.download_dir.setText(os.getcwd())  # 默认当前目录
        self.download_dir.setPlaceholderText("选择下载目录...")
        dir_row.addWidget(self.download_dir)
        self.browse_dir_btn = QPushButton("浏览...")
        self.browse_dir_btn.clicked.connect(self.browse_download_dir)
        dir_row.addWidget(self.browse_dir_btn)
        path_layout.addLayout(dir_row)

        # 文件名模板
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("文件名模板:"))
        self.filename_template = QLineEdit()
        self.filename_template.setPlaceholderText("{title}_{bvid} (留空使用默认)")
        name_row.addWidget(self.filename_template)
        path_layout.addLayout(name_row)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        layout.addStretch()
        return widget

    def create_options_tab(self):
        """创建下载选项标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 下载类型组
        type_group = QGroupBox("下载类型")
        type_layout = QVBoxLayout()

        self.download_type_group = QButtonGroup()

        self.type_video = QRadioButton("仅视频 (无音频)")
        self.type_video.setChecked(True)
        self.download_type_group.addButton(self.type_video, 1)

        self.type_audio = QRadioButton("仅音频")
        self.download_type_group.addButton(self.type_audio, 2)

        self.type_both = QRadioButton("视频+音频 (自动合并)")
        self.download_type_group.addButton(self.type_both, 3)

        self.type_cover = QRadioButton("仅封面图片")
        self.download_type_group.addButton(self.type_cover, 4)

        self.type_all = QRadioButton("视频+音频+封面")
        self.download_type_group.addButton(self.type_all, 5)

        type_layout.addWidget(self.type_video)
        type_layout.addWidget(self.type_audio)
        type_layout.addWidget(self.type_both)
        type_layout.addWidget(self.type_cover)
        type_layout.addWidget(self.type_all)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # 视频质量组
        quality_group = QGroupBox("视频质量")
        quality_layout = QVBoxLayout()

        quality_row = QHBoxLayout()
        quality_row.addWidget(QLabel("清晰度:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("自动选择 (推荐)", -1)
        self.quality_combo.addItem("8K 超高清", 127)
        self.quality_combo.addItem("4K 杜比视界", 126)
        self.quality_combo.addItem("4K 超清", 120)
        self.quality_combo.addItem("1080P 60帧", 116)
        self.quality_combo.addItem("1080P+ 高码率", 112)
        self.quality_combo.addItem("1080P 高清", 80)
        self.quality_combo.addItem("720P 高清", 64)
        self.quality_combo.addItem("480P 清晰", 32)
        self.quality_combo.addItem("360P 流畅", 16)
        quality_row.addWidget(self.quality_combo)
        quality_row.addStretch()
        quality_layout.addLayout(quality_row)

        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        # 高级选项组
        advanced_group = QGroupBox("高级选项")
        advanced_layout = QVBoxLayout()

        self.overwrite_files = QCheckBox("覆盖已存在文件")
        self.overwrite_files.setChecked(False)
        advanced_layout.addWidget(self.overwrite_files)

        self.auto_merge = QCheckBox("自动合并视频和音频")
        self.auto_merge.setChecked(True)
        advanced_layout.addWidget(self.auto_merge)

        self.show_progress = QCheckBox("显示详细进度")
        self.show_progress.setChecked(True)
        advanced_layout.addWidget(self.show_progress)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        layout.addStretch()
        return widget

    def create_output_tab(self):
        """创建进度输出标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 进度显示区域
        progress_group = QGroupBox("下载进度")
        progress_layout = QVBoxLayout()

        # 当前文件信息
        self.current_file_label = QLabel("当前文件: 无")
        progress_layout.addWidget(self.current_file_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        # 进度详情
        progress_detail_layout = QHBoxLayout()
        self.progress_percent = QLabel("0%")
        self.progress_percent.setStyleSheet("font-weight: bold; color: #3498db;")
        self.progress_size = QLabel("0 MB / 0 MB")
        progress_detail_layout.addWidget(self.progress_percent)
        progress_detail_layout.addStretch()
        progress_detail_layout.addWidget(self.progress_size)
        progress_layout.addLayout(progress_detail_layout)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # 输出信息组
        output_group = QGroupBox("下载输出")
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("下载过程的输出将在这里显示...")
        output_layout.addWidget(self.output_text)

        # 输出控制按钮
        output_buttons = QHBoxLayout()
        self.clear_output_btn = QPushButton("清空输出")
        self.clear_output_btn.clicked.connect(self.clear_output)
        self.save_log_btn = QPushButton("保存日志")
        self.save_log_btn.clicked.connect(self.save_log)
        output_buttons.addWidget(self.clear_output_btn)
        output_buttons.addWidget(self.save_log_btn)
        output_buttons.addStretch()
        output_layout.addLayout(output_buttons)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        return widget

    def browse_download_dir(self):
        """浏览选择下载目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择下载目录")
        if dir_path:
            self.download_dir.setText(dir_path)

    def update_login_status(self):
        """更新登录状态显示"""
        if self.downloader.is_logged_in:
            uname = self.downloader.user_info.get('uname', '未知用户')
            self.login_status.setText(f"已登录：{uname}")
            self.login_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.log_output(f"已登录: {uname}")
        else:
            self.login_status.setText("未登录")
            self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def login_bilibili(self):
        """扫码登录B站"""
        self.log_output("正在生成登录二维码...")
        self.login_btn.setEnabled(False)

        # 在新线程中执行登录
        login_thread = threading.Thread(target=self._do_login)
        login_thread.daemon = True
        login_thread.start()

    def _do_login(self):
        """执行登录操作"""
        try:
            success = self.downloader.qr_login()
            if success:
                # 在UI线程中更新状态
                self.update_login_status()
                self.log_output("登录成功!")
            else:
                self.log_output("登录失败!")
        except Exception as e:
            self.log_output(f"登录过程中出错: {str(e)}")

        # 重新启用登录按钮
        self.login_btn.setEnabled(True)

    def logout_bilibili(self):
        """退出登录"""
        reply = QMessageBox.question(self, "确认退出", "确定要退出登录吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = self.downloader.logout()
            if success:
                self.update_login_status()
                self.log_output("已退出登录")
            else:
                self.log_output("退出登录失败")

    def start_download(self):
        """开始下载"""
        # 验证输入
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "输入错误", "请输入BV号或视频URL")
            return

        # 获取下载类型
        download_type = str(self.download_type_group.checkedId())

        # 获取视频质量
        quality = self.quality_combo.currentData()
        if quality == -1:
            quality = None

        # 检查是否需要登录的高清选项
        need_login_qualities = [127, 126, 120, 116, 112, 80]
        if quality in need_login_qualities and not self.downloader.is_logged_in:
            reply = QMessageBox.question(
                self,
                "需要登录",
                f"您选择的清晰度需要登录才能下载。\n是否现在扫码登录？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.login_bilibili()
                return  # 等待登录完成后再下载
            else:
                # 用户选择不登录，自动降级到720P
                quality = 64
                self.log_output("已自动切换到720P清晰度（无需登录）")

        # 获取下载目录
        download_path = self.download_dir.text().strip()
        if not download_path:
            download_path = os.getcwd()

        # 检查目录是否存在
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except Exception as e:
                QMessageBox.warning(self, "目录错误", f"无法创建下载目录: {str(e)}")
                return

        # 重置进度显示
        self.reset_progress_display()

        # 禁用按钮
        self.download_btn.setEnabled(False)
        self.login_btn.setEnabled(False)

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # 切换到输出页
        self.tabs.setCurrentIndex(2)

        # 在工作线程中执行下载
        self.download_thread = DownloadWorker(
            self.downloader, url, quality, download_type, download_path
        )
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.log_signal.connect(self.log_output)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.file_progress_signal.connect(self.update_file_progress)
        self.download_thread.start()

    def reset_progress_display(self):
        """重置进度显示"""
        self.progress_bar.setValue(0)
        self.progress_percent.setText("0%")
        self.progress_size.setText("0 MB / 0 MB")
        self.current_file_label.setText("当前文件: 无")
        self.current_file = ""

    def update_progress(self, filename, progress):
        """更新下载进度"""
        self.progress_bar.setValue(progress)
        self.progress_percent.setText(f"{progress}%")

        if filename != self.current_file:
            self.current_file = filename
            self.current_file_label.setText(f"当前文件: {filename}")
            self.log_output(f"开始下载: {filename}")

    def update_file_progress(self, filename, downloaded, total):
        """更新文件下载进度详情"""
        if total > 0:
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.progress_size.setText(f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB")

    def log_output(self, message):
        """输出日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.append(f"[{timestamp}] {message}")

        # 自动滚动到底部
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.End)
        self.output_text.setTextCursor(cursor)

        # 更新状态栏
        self.status_label.setText(message)

    def download_finished(self, success, message):
        """下载完成处理"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)

        # 启用按钮
        self.download_btn.setEnabled(True)
        self.login_btn.setEnabled(True)

        # 显示完成消息
        self.log_output(message)

        if success:
            self.status_label.setText("下载完成")
            self.progress_percent.setText("100%")
            self.progress_percent.setStyleSheet("font-weight: bold; color: #27ae60;")
            QMessageBox.information(self, "成功", "视频下载完成！")
        else:
            self.status_label.setText("下载失败")
            self.progress_percent.setStyleSheet("font-weight: bold; color: #e74c3c;")
            QMessageBox.warning(self, "失败", "视频下载失败，请查看输出信息")

    def clear_output(self):
        """清空输出文本"""
        self.output_text.clear()

    def save_log(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "bilibili_download_log.txt", "Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.toPlainText())
                self.log_output(f"日志已保存到: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", f"无法保存日志: {str(e)}")

    def clear_settings(self):
        """清除所有设置"""
        reply = QMessageBox.question(self, "确认清除", "确定要清除所有设置吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 清除输入字段
            self.url_input.clear()
            self.download_dir.setText(os.getcwd())
            self.filename_template.clear()

            # 重置选项
            self.type_video.setChecked(True)
            self.quality_combo.setCurrentIndex(0)
            self.overwrite_files.setChecked(False)
            self.auto_merge.setChecked(True)
            self.show_progress.setChecked(True)

            # 重置登录状态
            self.login_status.setText("未登录")
            self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")

            # 清空输出和重置进度
            self.output_text.clear()
            self.reset_progress_display()

            self.log_output("设置已清除")


def main():
    app = QApplication(sys.argv)

    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = BiliDownloaderGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()