"""
翻译结果悬浮窗
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QCursor, QColor
from loguru import logger

from src.services.translation_service import TranslationService
from src.utils.config_loader import config


class TranslationWorker(QThread):
    """翻译工作线程"""
    finished = pyqtSignal(str)  # 翻译完成信号
    error = pyqtSignal(str)     # 错误信号

    def __init__(self, text: str, translation_service):
        super().__init__()
        self.text = text
        self.translation_service = translation_service

    def run(self):
        """执行翻译"""
        try:
            # 在线程中运行异步代码
            import asyncio

            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 执行异步翻译
                result = loop.run_until_complete(
                    self.translation_service.translate(self.text)
                )
                self.finished.emit(result.translation)
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"翻译失败: {e}")
            self.error.emit(str(e))


class PronunciationWorker(QThread):
    """发音工作线程"""
    finished = pyqtSignal(bool)  # 发音完成信号
    error = pyqtSignal(str)      # 错误信号

    def __init__(self, text: str, lang: str = "en"):
        super().__init__()
        self.text = text
        self.lang = lang

    def run(self):
        """执行发音"""
        try:
            import asyncio
            from src.core.pronunciation import PronunciationService

            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 执行异步发音
                service = PronunciationService()
                success = loop.run_until_complete(
                    service.pronounce(self.text, self.lang)
                )
                self.finished.emit(success)
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"发音失败: {e}")
            self.error.emit(str(e))


class PopupWindow(QWidget):
    """翻译结果悬浮窗"""

    def __init__(self):
        super().__init__()
        self.translation_service = TranslationService()
        self.current_text = ""
        self.translation_worker = None  # 翻译工作线程
        self.pronunciation_worker = None  # 发音工作线程

        # 拖动相关
        self._drag_pos = None
        self._is_dragging = False

        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        # 窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # 无边框
            Qt.WindowType.WindowStaysOnTopHint |     # 置顶
            Qt.WindowType.Tool                        # 不显示任务栏
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        
        # 设置尺寸
        self.setFixedWidth(config.ui.popup.width)
        self.setMaximumHeight(config.ui.popup.max_height)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 内容容器（带圆角和阴影）
        self.container = QFrame()
        self.container.setObjectName("popupContainer")
        self.container.setStyleSheet("""
            #popupContainer {
                background: white;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(12)
        
        # 标题栏
        header = self._create_header()
        container_layout.addWidget(header)
        
        # 原文
        self.source_label = QLabel()
        self.source_label.setWordWrap(True)
        self.source_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
                padding: 8px;
                background: #f9fafb;
                border-radius: 6px;
            }
        """)
        container_layout.addWidget(self.source_label)
        
        # 翻译结果
        self.translation_label = QLabel()
        self.translation_label.setWordWrap(True)
        self.translation_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.translation_label.setStyleSheet("""
            QLabel {
                color: #111827;
                font-size: 16px;
                padding: 12px;
                line-height: 1.6;
            }
        """)
        container_layout.addWidget(self.translation_label)
        
        # 底部操作栏
        actions = self._create_actions()
        container_layout.addWidget(actions)
        
        layout.addWidget(self.container)
    
    def _create_header(self) -> QWidget:
        """创建标题栏"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel("翻译")
        title.setStyleSheet("font-size: 13px; color: #6b7280; font-weight: 500;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 20px;
                color: #9ca3af;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #f3f4f6;
                color: #6b7280;
            }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        return header
    
    def _create_actions(self) -> QWidget:
        """创建操作按钮"""
        actions = QWidget()
        layout = QHBoxLayout(actions)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)

        # 收藏按钮
        save_btn = self._create_action_button("⭐", "收藏")
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        # 复制按钮
        copy_btn = self._create_action_button("📋", "复制")
        copy_btn.clicked.connect(self._on_copy)
        layout.addWidget(copy_btn)

        # 发音按钮
        pronounce_btn = self._create_action_button("🔊", "发音")
        pronounce_btn.clicked.connect(self._on_pronounce)
        layout.addWidget(pronounce_btn)

        layout.addStretch()

        return actions
    
    def _create_action_button(self, icon: str, text: str) -> QPushButton:
        """创建操作按钮"""
        btn = QPushButton(f"{icon} {text}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                color: #374151;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
            QPushButton:pressed {
                background: #d1d5db;
            }
        """)
        return btn
    
    def show_translation(self, text: str):
        """显示翻译结果"""
        self.current_text = text
        
        # 显示加载状态
        self.source_label.setText(text)
        self.translation_label.setText("翻译中...")
        self.show_at_cursor()
        
        # 停止之前的翻译任务
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.quit()
            self.translation_worker.wait()
        
        # 创建新的翻译线程
        self.translation_worker = TranslationWorker(text, self.translation_service)
        self.translation_worker.finished.connect(self._on_translation_finished)
        self.translation_worker.error.connect(self._on_translation_error)
        self.translation_worker.start()
    
    def _on_translation_finished(self, translation: str):
        """翻译完成回调（在主线程中执行）"""
        # 由于使用了 pyqtSignal，这个回调会自动在主线程执行
        logger.info(f"翻译完成，更新UI: {translation[:50]}...")
        self.translation_label.setText(translation)
        self.adjustSize()
    
    def _on_translation_error(self, error: str):
        """翻译错误回调（在主线程中执行）"""
        logger.error(f"翻译失败: {error}")
        self.translation_label.setText(f"翻译失败: {error}")
    
    def show_at_cursor(self):
        """在鼠标位置显示"""
        cursor_pos = QCursor.pos()
        
        # 偏移量
        offset_x = config.ui.popup.offset_x
        offset_y = config.ui.popup.offset_y
        
        # 计算位置（确保不超出屏幕）
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        
        x = cursor_pos.x() + offset_x
        y = cursor_pos.y() + offset_y
        
        # 边界检查
        if x + self.width() > screen.right():
            x = screen.right() - self.width() - 20
        if y + self.height() > screen.bottom():
            y = screen.bottom() - self.height() - 20
        
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
    
    def _on_save(self):
        """收藏按钮点击"""
        try:
            from src.data.models import Entry
            from src.data.repository import EntryRepository
            
            # 创建词条
            entry = Entry(
                source_text=self.current_text,
                translation=self.translation_label.text(),
                source_lang="auto",
                target_lang="zh"
            )
            
            # 保存到数据库
            repo = EntryRepository()
            repo.save(entry)
            
            logger.info(f"词条已收藏: {self.current_text}")
            
            # 提示用户
            from PyQt6.QtWidgets import QToolTip
            from PyQt6.QtGui import QCursor
            QToolTip.showText(QCursor.pos(), "已收藏！", self)
        
        except Exception as e:
            logger.error(f"收藏失败: {e}")
    
    def _on_copy(self):
        """复制按钮点击"""
        import pyperclip
        translation = self.translation_label.text()
        if translation and translation != "翻译中...":
            pyperclip.copy(translation)
            logger.info("已复制翻译结果")
    
    def _on_pronounce(self):
        """发音按钮点击"""
        try:
            # 获取要发音的文本（原文）
            text = self.current_text
            if not text:
                logger.warning("没有可发音的文本")
                return

            # 停止之前的发音任务
            if self.pronunciation_worker and self.pronunciation_worker.isRunning():
                self.pronunciation_worker.quit()
                self.pronunciation_worker.wait()

            # 检测语言
            from src.core.language_detector import LanguageDetector
            detector = LanguageDetector()
            lang = detector.detect(text)

            # 创建新的发音线程
            self.pronunciation_worker = PronunciationWorker(text, lang)
            self.pronunciation_worker.finished.connect(self._on_pronunciation_finished)
            self.pronunciation_worker.error.connect(self._on_pronunciation_error)
            self.pronunciation_worker.start()

            logger.info(f"开始发音: {text[:20]}... (语言: {lang})")

        except Exception as e:
            logger.error(f"发音失败: {e}")

    def _on_pronunciation_finished(self, success: bool):
        """发音完成回调"""
        if success:
            logger.info("发音完成")
        else:
            logger.warning("发音失败")

    def _on_pronunciation_error(self, error: str):
        """发音错误回调"""
        logger.error(f"发音错误: {error}")
        # 可选: 显示用户提示
        from PyQt6.QtWidgets import QToolTip
        from PyQt6.QtGui import QCursor
        QToolTip.showText(QCursor.pos(), "发音失败，请检查网络或edge-tts安装", self)
    
    def keyPressEvent(self, event):
        """按键事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖动"""
        from PyQt6.QtCore import Qt
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        from PyQt6.QtCore import Qt
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖动"""
        from PyQt6.QtCore import Qt
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

