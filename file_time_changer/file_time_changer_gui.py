import sys
import os
import ctypes
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QDateTimeEdit, QMessageBox, QFrame, QGroupBox, QCheckBox,
                             QProgressBar, QTextEdit, QTabWidget, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QDateTime, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import file_time_changer  # 直接引用你提供的模块

class FileTimeChangerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("文件时间修改工具")
        self.setGeometry(300, 200, 1000, 700)
        self.setMinimumSize(900, 600)
        
        # 设置窗口图标 (使用系统图标或自定义)
        try:
            self.setWindowIcon(QIcon("clock_icon.ico"))
        except:
            pass
        
        # 设置现代化样式
        self.set_modern_style()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("文件时间修改工具")
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
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 单文件修改选项卡
        single_file_tab = self.create_single_file_tab()
        tab_widget.addTab(single_file_tab, "单文件修改")
        
        # 批量修改选项卡
        batch_tab = self.create_batch_tab()
        tab_widget.addTab(batch_tab, "批量修改")
        
        # 日志区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        main_layout.addWidget(log_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        self.log("文件时间修改工具已启动")
        
    def create_single_file_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        file_selector_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择文件或文件夹...")
        file_selector_layout.addWidget(self.file_path_edit)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_file)
        file_selector_layout.addWidget(self.browse_button)
        
        file_layout.addLayout(file_selector_layout)
        layout.addWidget(file_group)
        
        # 时间设置区域
        time_group = QGroupBox("时间设置")
        time_layout = QVBoxLayout(time_group)
        
        # 创建时间
        creation_layout = QHBoxLayout()
        self.creation_check = QCheckBox("修改创建时间:")
        self.creation_check.setChecked(True)
        creation_layout.addWidget(self.creation_check)
        
        self.creation_datetime = QDateTimeEdit()
        self.creation_datetime.setDateTime(QDateTime.currentDateTime())
        self.creation_datetime.setCalendarPopup(True)
        creation_layout.addWidget(self.creation_datetime)
        creation_layout.addStretch()
        
        time_layout.addLayout(creation_layout)
        
        # 修改时间
        modified_layout = QHBoxLayout()
        self.modified_check = QCheckBox("修改最后修改时间:")
        self.modified_check.setChecked(True)
        modified_layout.addWidget(self.modified_check)
        
        self.modified_datetime = QDateTimeEdit()
        self.modified_datetime.setDateTime(QDateTime.currentDateTime())
        self.modified_datetime.setCalendarPopup(True)
        modified_layout.addWidget(self.modified_datetime)
        modified_layout.addStretch()
        
        time_layout.addLayout(modified_layout)
        
        # 访问时间
        access_layout = QHBoxLayout()
        self.access_check = QCheckBox("修改最后访问时间:")
        self.access_check.setChecked(True)
        access_layout.addWidget(self.access_check)
        
        self.access_datetime = QDateTimeEdit()
        self.access_datetime.setDateTime(QDateTime.currentDateTime())
        self.access_datetime.setCalendarPopup(True)
        access_layout.addWidget(self.access_datetime)
        access_layout.addStretch()
        
        time_layout.addLayout(access_layout)
        
        # 快速设置按钮
        quick_buttons_layout = QHBoxLayout()
        current_time_btn = QPushButton("设为当前时间")
        current_time_btn.clicked.connect(self.set_current_time)
        quick_buttons_layout.addWidget(current_time_btn)
        
        clear_time_btn = QPushButton("清空选择")
        clear_time_btn.clicked.connect(self.clear_time_selection)
        quick_buttons_layout.addWidget(clear_time_btn)
        
        time_layout.addLayout(quick_buttons_layout)
        
        layout.addWidget(time_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("应用修改")
        self.apply_button.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def create_batch_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 文件夹选择
        folder_group = QGroupBox("批量操作设置")
        folder_layout = QVBoxLayout(folder_group)
        
        folder_selector_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("选择包含文件的文件夹...")
        folder_selector_layout.addWidget(self.folder_path_edit)
        
        self.browse_folder_button = QPushButton("浏览文件夹...")
        self.browse_folder_button.clicked.connect(self.browse_folder)
        folder_selector_layout.addWidget(self.browse_folder_button)
        
        folder_layout.addLayout(folder_selector_layout)
        
        # 文件过滤
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("文件过滤:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("例如: *.txt, *.docx (留空表示所有文件)")
        filter_layout.addWidget(self.filter_edit)
        
        folder_layout.addLayout(filter_layout)
        
        # 递归选项
        self.recursive_check = QCheckBox("包含子文件夹")
        self.recursive_check.setChecked(True)
        folder_layout.addWidget(self.recursive_check)
        
        # 文件列表
        files_label = QLabel("文件列表:")
        folder_layout.addWidget(files_label)
        
        self.files_list = QListWidget()
        folder_layout.addWidget(self.files_list)
        
        # 刷新文件列表按钮
        refresh_button = QPushButton("刷新文件列表")
        refresh_button.clicked.connect(self.refresh_file_list)
        folder_layout.addWidget(refresh_button)
        
        layout.addWidget(folder_group)
        
        # 批量时间设置
        batch_time_group = QGroupBox("批量时间设置")
        batch_time_layout = QVBoxLayout(batch_time_group)
        
        # 批量时间选择
        batch_datetime_layout = QHBoxLayout()
        batch_datetime_layout.addWidget(QLabel("设置时间:"))
        self.batch_datetime = QDateTimeEdit()
        self.batch_datetime.setDateTime(QDateTime.currentDateTime())
        self.batch_datetime.setCalendarPopup(True)
        batch_datetime_layout.addWidget(self.batch_datetime)
        batch_datetime_layout.addStretch()
        
        batch_time_layout.addLayout(batch_datetime_layout)
        
        # 时间类型选项
        time_types_layout = QHBoxLayout()
        self.batch_creation_check = QCheckBox("修改创建时间")
        self.batch_creation_check.setChecked(True)
        time_types_layout.addWidget(self.batch_creation_check)
        
        self.batch_modified_check = QCheckBox("修改修改时间")
        self.batch_modified_check.setChecked(True)
        time_types_layout.addWidget(self.batch_modified_check)
        
        self.batch_access_check = QCheckBox("修改访问时间")
        self.batch_access_check.setChecked(True)
        time_types_layout.addWidget(self.batch_access_check)
        
        batch_time_layout.addLayout(time_types_layout)
        
        layout.addWidget(batch_time_group)
        
        # 批量操作按钮
        batch_button_layout = QHBoxLayout()
        self.batch_apply_button = QPushButton("执行批量修改")
        self.batch_apply_button.clicked.connect(self.apply_batch_changes)
        batch_button_layout.addWidget(self.batch_apply_button)
        
        layout.addLayout(batch_button_layout)
        layout.addStretch()
        
        return widget
    
    def set_modern_style(self):
        # 设置现代化样式表，与PyInstaller GUI保持一致
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 11px;
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
            QLineEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2c3e50;
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
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #2c3e50;
                background-color: #2c3e50;
                border-radius: 2px;
            }
            QDateTimeEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px;
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
                padding: 8px;
            }
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
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
        """)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.log(f"已选择文件: {file_path}")
    
    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择文件夹"
        )
        if folder_path:
            self.folder_path_edit.setText(folder_path)
            self.refresh_file_list()
    
    def refresh_file_list(self):
        folder_path = self.folder_path_edit.text().strip()
        if not folder_path or not os.path.exists(folder_path):
            return
        
        self.files_list.clear()
        
        # 获取文件过滤器
        file_filter = self.filter_edit.text().strip()
        if file_filter:
            filters = [f.strip() for f in file_filter.split(',')]
        else:
            filters = ['*']
        
        # 收集文件
        files = []
        if self.recursive_check.isChecked():
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    for file_filter in filters:
                        if filename.lower().endswith(file_filter.replace('*', '').lower()) or file_filter == '*':
                            files.append(os.path.join(root, filename))
                            break
        else:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    for file_filter in filters:
                        if filename.lower().endswith(file_filter.replace('*', '').lower()) or file_filter == '*':
                            files.append(file_path)
                            break
        
        # 添加到列表
        for file_path in files:
            item = QListWidgetItem(file_path)
            self.files_list.addItem(item)
        
        self.log(f"已找到 {len(files)} 个文件")
    
    def set_current_time(self):
        current_time = QDateTime.currentDateTime()
        self.creation_datetime.setDateTime(current_time)
        self.modified_datetime.setDateTime(current_time)
        self.access_datetime.setDateTime(current_time)
        self.log("已将时间设置为当前时间")
    
    def clear_time_selection(self):
        self.creation_check.setChecked(False)
        self.modified_check.setChecked(False)
        self.access_check.setChecked(False)
        self.log("已清空时间选择")
    
    def apply_changes(self):
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "错误", "请先选择文件或文件夹")
            return
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "选择的文件或文件夹不存在")
            return
        
        # 检查是否至少选择了一个时间选项
        if not (self.creation_check.isChecked() or 
                self.modified_check.isChecked() or 
                self.access_check.isChecked()):
            QMessageBox.warning(self, "错误", "请至少选择一个要修改的时间选项")
            return
        
        try:
            # 准备时间参数
            creation_time = None
            last_write_time = None
            last_access_time = None
            
            if self.creation_check.isChecked():
                creation_time = self.creation_datetime.dateTime().toPyDateTime()
            
            if self.modified_check.isChecked():
                last_write_time = self.modified_datetime.dateTime().toPyDateTime()
            
            if self.access_check.isChecked():
                last_access_time = self.access_datetime.dateTime().toPyDateTime()
            
            # 显示进度
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(50)
            QApplication.processEvents()
            
            # 调用file_time_changer模块
            file_time_changer.set_file_time(
                file_path, 
                creation_time, 
                last_access_time, 
                last_write_time
            )
            
            self.progress_bar.setValue(100)
            QTimer.singleShot(500, lambda: self.progress_bar.setVisible(False))
            
            self.log(f"成功修改文件时间: {file_path}")
            QMessageBox.information(self, "成功", "文件时间修改成功")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            error_msg = f"修改文件时间时出错: {str(e)}"
            self.log(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def apply_batch_changes(self):
        folder_path = self.folder_path_edit.text().strip()
        if not folder_path:
            QMessageBox.warning(self, "错误", "请先选择文件夹")
            return
        
        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "错误", "选择的文件夹不存在")
            return
        
        if self.files_list.count() == 0:
            QMessageBox.warning(self, "错误", "没有找到可操作的文件")
            return
        
        if not (self.batch_creation_check.isChecked() or 
                self.batch_modified_check.isChecked() or 
                self.batch_access_check.isChecked()):
            QMessageBox.warning(self, "错误", "请至少选择一个要修改的时间选项")
            return
        
        try:
            # 显示进度
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, self.files_list.count())
            
            # 获取设置的时间
            target_time = self.batch_datetime.dateTime().toPyDateTime()
            
            # 处理每个文件
            success_count = 0
            for i in range(self.files_list.count()):
                file_path = self.files_list.item(i).text()
                
                # 准备时间参数
                creation_time = target_time if self.batch_creation_check.isChecked() else None
                last_write_time = target_time if self.batch_modified_check.isChecked() else None
                last_access_time = target_time if self.batch_access_check.isChecked() else None
                
                try:
                    # 调用file_time_changer模块
                    file_time_changer.set_file_time(
                        file_path, 
                        creation_time, 
                        last_access_time, 
                        last_write_time
                    )
                    success_count += 1
                    self.log(f"成功修改: {os.path.basename(file_path)}")
                except Exception as e:
                    self.log(f"失败: {os.path.basename(file_path)} - {str(e)}")
                
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()
            
            self.progress_bar.setVisible(False)
            
            result_msg = f"批量修改完成: 成功 {success_count}/{self.files_list.count()} 个文件"
            self.log(result_msg)
            QMessageBox.information(self, "完成", result_msg)
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            error_msg = f"批量修改时出错: {str(e)}"
            self.log(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        self.statusBar().showMessage(message)
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

def main():
    # 启用高DPI缩放
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("文件时间修改工具")
    app.setApplicationVersion("1.0")
    
    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 创建并显示主窗口
    window = FileTimeChangerUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()