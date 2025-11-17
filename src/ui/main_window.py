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
from src.ui.review_window import ReviewWindow
from src.services.review_service import ReviewService


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.entry_repo = EntryRepository()
        self.review_service = ReviewService()
        self.review_window = ReviewWindow()
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

        # 复习标签页
        review_tab = self._create_review_tab()
        tabs.addTab(review_tab, "🔄 复习")

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

    def _create_review_tab(self) -> QWidget:
        """创建复习标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("📖 智能复习系统")
        title_font = title.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # 复习统计卡片
        stats = self.review_service.get_review_statistics()

        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_widget)

        # 统计数据
        stats_info = QLabel(
            f"总词条: {stats.get('total_count', 0)} | "
            f"待复习: {stats.get('due_count', 0)} | "
            f"已掌握: {stats.get('mastered_count', 0)} | "
            f"今日已复习: {stats.get('reviewed_today', 0)}"
        )
        stats_info.setStyleSheet("font-size: 14px; color: #495057;")
        stats_layout.addWidget(stats_info)

        # 进度说明
        mastered_pct = (stats.get('mastered_count', 0) / stats.get('total_count', 1)) * 100
        progress_label = QLabel(f"掌握率: {mastered_pct:.1f}%")
        progress_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #28a745;")
        stats_layout.addWidget(progress_label)

        layout.addWidget(stats_widget)

        # 待复习列表
        reviews_by_urgency = self.review_service.get_reviews_by_urgency()

        # 逾期
        if reviews_by_urgency['overdue']:
            overdue_label = QLabel(f"⚠️ 逾期复习 ({len(reviews_by_urgency['overdue'])} 个)")
            overdue_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #dc3545;")
            layout.addWidget(overdue_label)

            overdue_btn = QPushButton(f"开始复习逾期词条 ({len(reviews_by_urgency['overdue'])})")
            overdue_btn.setMinimumHeight(45)
            overdue_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            overdue_btn.clicked.connect(lambda: self._start_review(reviews_by_urgency['overdue']))
            layout.addWidget(overdue_btn)

        # 今天
        if reviews_by_urgency['today']:
            today_label = QLabel(f"📅 今日复习 ({len(reviews_by_urgency['today'])} 个)")
            today_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #007bff;")
            layout.addWidget(today_label)

            today_btn = QPushButton(f"开始今日复习 ({len(reviews_by_urgency['today'])})")
            today_btn.setMinimumHeight(45)
            today_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            today_btn.clicked.connect(lambda: self._start_review(reviews_by_urgency['today']))
            layout.addWidget(today_btn)

        # 即将到期
        if reviews_by_urgency['soon']:
            soon_label = QLabel(f"🔜 即将到期 ({len(reviews_by_urgency['soon'])} 个)")
            soon_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffc107;")
            layout.addWidget(soon_label)

            soon_btn = QPushButton(f"提前复习 ({len(reviews_by_urgency['soon'])})")
            soon_btn.setMinimumHeight(45)
            soon_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: #212529;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
            """)
            soon_btn.clicked.connect(lambda: self._start_review(reviews_by_urgency['soon']))
            layout.addWidget(soon_btn)

        # 如果没有待复习
        if not (reviews_by_urgency['overdue'] or reviews_by_urgency['today']):
            no_review_label = QLabel("✅ 目前没有需要复习的词条\n\n继续学习新单词，系统会在合适的时间提醒你复习！")
            no_review_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_review_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #6c757d;
                    padding: 40px;
                    background-color: #e9ecef;
                    border-radius: 10px;
                }
            """)
            layout.addWidget(no_review_label)

        layout.addStretch()

        return widget

    def _start_review(self, entries):
        """
        开始复习

        Args:
            entries: 词条列表
        """
        try:
            if not entries:
                logger.warning("没有待复习的词条")
                return

            # 启动复习窗口
            self.review_window.start_review(entries)

        except Exception as e:
            logger.error(f"启动复习失败: {e}")

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

