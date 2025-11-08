"""
主窗口
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QLineEdit,
    QTabWidget
)
from PyQt6.QtCore import Qt
from loguru import logger

from src.data.repository import EntryRepository
from src.utils.config_loader import config
from src.ui.settings_dialog import SettingsDialog
from src.ui.entry_detail_dialog import EntryDetailDialog
from src.ui.statistics_window import StatisticsWindow


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.entry_repo = EntryRepository()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(config.app.name)
        self.resize(config.ui.main_window.width, config.ui.main_window.height)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部工具栏
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # 主要内容区
        tabs = self._create_tabs()
        layout.addWidget(tabs)
    
    def _create_toolbar(self) -> QWidget:
        """创建顶部工具栏"""
        toolbar = QWidget()
        toolbar.setStyleSheet("""
            QWidget {
                background: white;
                border-bottom: 1px solid #e5e7eb;
                padding: 12px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        
        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索...")
        self.search_box.setFixedWidth(300)
        self.search_box.textChanged.connect(self._on_search)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        layout.addWidget(self.search_box)
        
        layout.addStretch()
        
        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.clicked.connect(self._open_settings)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """)
        layout.addWidget(settings_btn)
        
        return toolbar
    
    def _create_tabs(self) -> QTabWidget:
        """创建标签页"""
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                padding: 12px 24px;
                font-size: 14px;
                border: none;
                background: transparent;
            }
            QTabBar::tab:selected {
                color: #3b82f6;
                border-bottom: 2px solid #3b82f6;
            }
        """)
        
        # 词库标签页
        library_tab = self._create_library_tab()
        tabs.addTab(library_tab, "📚 词库")
        
        # 统计标签页
        stats_tab = self._create_stats_tab()
        tabs.addTab(stats_tab, "📊 统计")
        
        return tabs
    
    def _create_library_tab(self) -> QWidget:
        """创建词库标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 词条列表
        self.entry_list_widget = QListWidget()
        self.entry_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f3f4f6;
            }
            QListWidget::item:hover {
                background: #f9fafb;
            }
            QListWidget::item:selected {
                background: #eff6ff;
                color: #1e40af;
            }
        """)
        
        # 双击事件
        self.entry_list_widget.itemDoubleClicked.connect(self._on_entry_double_clicked)
        
        # 加载词条
        self._load_entries(self.entry_list_widget)
        
        layout.addWidget(self.entry_list_widget)
        
        return widget
    
    def _create_stats_tab(self) -> QWidget:
        """创建统计标签页"""
        # 直接嵌入统计窗口
        stats_widget = StatisticsWindow()
        return stats_widget
    
    def _load_entries(self, list_widget: QListWidget):
        """加载词条列表"""
        try:
            self.entries = self.entry_repo.get_all(limit=100)
            
            for entry in self.entries:
                item_text = f"{entry.source_text[:50]} → {entry.translation[:50]}"
                list_widget.addItem(item_text)
            
            logger.debug(f"加载了 {len(self.entries)} 条记录")
        
        except Exception as e:
            logger.error(f"加载词条失败: {e}")
            self.entries = []
    
    def _open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _on_entry_double_clicked(self, item):
        """词条双击事件"""
        try:
            # 获取对应的词条
            index = self.entry_list_widget.row(item)
            if 0 <= index < len(self.entries):
                entry = self.entries[index]
                
                # 打开详情对话框
                dialog = EntryDetailDialog(entry, self)
                if dialog.exec():
                    # 刷新列表
                    self.entry_list_widget.clear()
                    self._load_entries(self.entry_list_widget)
        
        except Exception as e:
            logger.error(f"打开词条详情失败: {e}")
    
    def _on_search(self, text: str):
        """搜索框文本变化"""
        try:
            self.entry_list_widget.clear()
            
            if not text:
                # 空搜索，显示全部
                self._load_entries(self.entry_list_widget)
            else:
                # 搜索
                results = self.entry_repo.search(text, limit=100)
                self.entries = results
                
                for entry in results:
                    item_text = f"{entry.source_text[:50]} → {entry.translation[:50]}"
                    self.entry_list_widget.addItem(item_text)
                
                logger.debug(f"搜索到 {len(results)} 条记录")
        
        except Exception as e:
            logger.error(f"搜索失败: {e}")

