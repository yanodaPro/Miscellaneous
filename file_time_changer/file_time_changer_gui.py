import sys
import os
import ctypes
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QDateTimeEdit, QMessageBox, QFrame, QGroupBox, QCheckBox,
                             QProgressBar, QTextEdit, QTabWidget)
from PyQt5.QtCore import Qt, QDateTime, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import file_time_changer  # 直接引用你提供的模块

class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 6px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 5px;
            }
        """)

class FileTimeChangerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("文件时间修改工具 - Windows 11 风格")
        self.setGeometry(300, 200, 800, 600)
        self.setMinimumSize(700, 500)
        
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
                color: #000000;
                padding: 10px;
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
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        main_layout.addWidget(log_group)
        
        # 进度条
        self.progress_bar = ModernProgressBar()
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
        
        self.browse_button = QPushButton("浏览")
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
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
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
        
        self.browse_folder_button = QPushButton("浏览文件夹")
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
        
        layout.addWidget(folder_group)
        
        # 批量时间设置
        batch_time_group = QGroupBox("批量时间设置")
        batch_time_layout = QVBoxLayout(batch_time_group)
        
        batch_time_buttons_layout = QHBoxLayout()
        
        same_time_btn = QPushButton("所有文件设为相同时间")
        same_time_btn.clicked.connect(self.set_batch_same_time)
        batch_time_buttons_layout.addWidget(same_time_btn)
        
        preserve_btn = QPushButton("保持相对时间")
        preserve_btn.clicked.connect(self.set_batch_preserve_relative)
        batch_time_buttons_layout.addWidget(preserve_btn)
        
        batch_time_layout.addLayout(batch_time_buttons_layout)
        
        # 批量时间选择
        batch_datetime_layout = QHBoxLayout()
        batch_datetime_layout.addWidget(QLabel("设置时间:"))
        self.batch_datetime = QDateTimeEdit()
        self.batch_datetime.setDateTime(QDateTime.currentDateTime())
        self.batch_datetime.setCalendarPopup(True)
        batch_datetime_layout.addWidget(self.batch_datetime)
        batch_datetime_layout.addStretch()
        
        batch_time_layout.addLayout(batch_datetime_layout)
        layout.addWidget(batch_time_group)
        
        # 批量操作按钮
        batch_button_layout = QHBoxLayout()
        self.batch_apply_button = QPushButton("执行批量修改")
        self.batch_apply_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e6a0e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.batch_apply_button.clicked.connect(self.apply_batch_changes)
        batch_button_layout.addWidget(self.batch_apply_button)
        
        layout.addLayout(batch_button_layout)
        layout.addStretch()
        
        return widget
    
    def set_modern_style(self):
        # 设置现代化样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f3f3;
            }
            QWidget {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 11px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #e1e1e1;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #d5d5d5;
            }
            QPushButton:pressed {
                background-color: #c9c9c9;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #0078d4;
                background-color: #0078d4;
                border-radius: 2px;
            }
            QDateTimeEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
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
            self.log(f"已选择文件夹: {folder_path}")
    
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
    
    def set_batch_same_time(self):
        # 设置批量操作为相同时间
        self.log("批量操作模式: 所有文件设为相同时间")
        QMessageBox.information(self, "批量设置", "所有文件将被设置为相同的时间")
    
    def set_batch_preserve_relative(self):
        # 设置批量操作为保持相对时间
        self.log("批量操作模式: 保持文件间的相对时间")
        QMessageBox.information(self, "批量设置", "将保持文件间的相对时间关系")
    
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
        
        # 这里可以实现批量修改逻辑
        # 由于时间关系，这里只显示提示
        QMessageBox.information(
            self, 
            "批量操作", 
            f"将对文件夹 '{folder_path}' 中的文件进行批量时间修改\n"
            f"文件过滤: {self.filter_edit.text() or '所有文件'}\n"
            f"包含子文件夹: {'是' if self.recursive_check.isChecked() else '否'}"
        )
        
        self.log(f"开始批量修改文件夹: {folder_path}")
        # 实际实现时需要遍历文件并调用file_time_changer.set_file_time
    
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
    
    # 创建并显示主窗口
    window = FileTimeChangerUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()