"""
复习窗口
提供卡片式复习界面，支持SM-2间隔重复算法
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from loguru import logger

from src.data.models import Entry
from src.services.review_service import ReviewService


class ReviewWindow(QWidget):
    """复习窗口"""

    review_completed = pyqtSignal()  # 复习完成信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.review_service = ReviewService()

        # 复习数据
        self.entries_to_review = []
        self.current_index = 0
        self.current_entry = None
        self.is_showing_answer = False

        # 统计
        self.correct_count = 0
        self.total_count = 0

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("复习")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 1. 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        layout.addWidget(self.progress_bar)

        # 2. 统计信息
        self.stats_label = QLabel("准备开始复习...")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)

        # 3. 卡片区域
        card_layout = QVBoxLayout()
        card_layout.setSpacing(15)

        # 问题/答案显示
        self.question_label = QLabel("准备就绪")
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setWordWrap(True)
        question_font = QFont()
        question_font.setPointSize(24)
        question_font.setBold(True)
        self.question_label.setFont(question_font)
        self.question_label.setMinimumHeight(150)
        self.question_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        card_layout.addWidget(self.question_label)

        # 答案区域（初始隐藏）
        self.answer_label = QLabel("")
        self.answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer_label.setWordWrap(True)
        answer_font = QFont()
        answer_font.setPointSize(18)
        self.answer_label.setFont(answer_font)
        self.answer_label.setMinimumHeight(100)
        self.answer_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e9;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.answer_label.hide()
        card_layout.addWidget(self.answer_label)

        # 附加信息（音标、例句等）
        self.extra_label = QLabel("")
        self.extra_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.extra_label.setWordWrap(True)
        self.extra_label.setStyleSheet("""
            QLabel {
                background-color: #fff3e0;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                color: #666;
            }
        """)
        self.extra_label.hide()
        card_layout.addWidget(self.extra_label)

        layout.addLayout(card_layout)

        # 4. 显示答案按钮
        self.show_answer_btn = QPushButton("显示答案 (Space)")
        self.show_answer_btn.setMinimumHeight(45)
        self.show_answer_btn.clicked.connect(self._show_answer)
        self.show_answer_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(self.show_answer_btn)

        # 5. 评分按钮组（初始隐藏）
        rating_layout = QHBoxLayout()
        rating_layout.setSpacing(10)

        self.forgot_btn = QPushButton("完全忘记 (1)")
        self.forgot_btn.setMinimumHeight(45)
        self.forgot_btn.clicked.connect(lambda: self._rate_answer(False, "hard"))
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        self.hard_btn = QPushButton("困难 (2)")
        self.hard_btn.setMinimumHeight(45)
        self.hard_btn.clicked.connect(lambda: self._rate_answer(True, "hard"))
        self.hard_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)

        self.normal_btn = QPushButton("一般 (3)")
        self.normal_btn.setMinimumHeight(45)
        self.normal_btn.clicked.connect(lambda: self._rate_answer(True, "normal"))
        self.normal_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)

        self.easy_btn = QPushButton("简单 (4)")
        self.easy_btn.setMinimumHeight(45)
        self.easy_btn.clicked.connect(lambda: self._rate_answer(True, "easy"))
        self.easy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)

        rating_layout.addWidget(self.forgot_btn)
        rating_layout.addWidget(self.hard_btn)
        rating_layout.addWidget(self.normal_btn)
        rating_layout.addWidget(self.easy_btn)

        self.rating_widget = QWidget()
        self.rating_widget.setLayout(rating_layout)
        self.rating_widget.hide()
        layout.addWidget(self.rating_widget)

        # 6. 底部操作按钮
        bottom_layout = QHBoxLayout()

        self.skip_btn = QPushButton("跳过")
        self.skip_btn.clicked.connect(self._skip_current)
        bottom_layout.addWidget(self.skip_btn)

        bottom_layout.addStretch()

        self.quit_btn = QPushButton("结束复习")
        self.quit_btn.clicked.connect(self._quit_review)
        bottom_layout.addWidget(self.quit_btn)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def start_review(self, entries=None):
        """
        开始复习

        Args:
            entries: 词条列表（None则自动获取待复习词条）
        """
        try:
            # 获取待复习词条
            if entries is None:
                entries = self.review_service.get_due_reviews(limit=50)

            if not entries:
                QMessageBox.information(
                    self,
                    "提示",
                    "暂无需要复习的词条！\n\n继续保持学习，词条会在合适的时间提醒你复习。"
                )
                return

            self.entries_to_review = entries
            self.current_index = 0
            self.correct_count = 0
            self.total_count = len(entries)

            # 更新进度条
            self.progress_bar.setMaximum(self.total_count)
            self.progress_bar.setValue(0)

            # 显示第一个词条
            self._show_next_entry()

            # 显示窗口
            self.show()
            self.activateWindow()

            logger.info(f"开始复习: 共 {self.total_count} 个词条")

        except Exception as e:
            logger.error(f"开始复习失败: {e}")
            QMessageBox.critical(self, "错误", f"开始复习失败: {e}")

    def _show_next_entry(self):
        """显示下一个词条"""
        if self.current_index >= len(self.entries_to_review):
            self._finish_review()
            return

        self.current_entry = self.entries_to_review[self.current_index]
        self.is_showing_answer = False

        # 更新UI
        self.question_label.setText(self.current_entry.source_text)
        self.answer_label.hide()
        self.extra_label.hide()
        self.show_answer_btn.show()
        self.rating_widget.hide()

        # 更新统计
        self._update_stats()

        logger.debug(f"显示词条 {self.current_index + 1}/{self.total_count}: {self.current_entry.source_text}")

    def _show_answer(self):
        """显示答案"""
        if not self.current_entry or self.is_showing_answer:
            return

        self.is_showing_answer = True

        # 显示翻译
        self.answer_label.setText(self.current_entry.translation)
        self.answer_label.show()

        # 显示附加信息
        extra_info = []
        if self.current_entry.pronunciation:
            extra_info.append(f"📢 {self.current_entry.pronunciation}")
        if self.current_entry.explanation:
            extra_info.append(f"📖 {self.current_entry.explanation}")
        if self.current_entry.context:
            extra_info.append(f"💬 {self.current_entry.context[:100]}")

        if extra_info:
            self.extra_label.setText("\n".join(extra_info))
            self.extra_label.show()

        # 切换按钮
        self.show_answer_btn.hide()
        self.rating_widget.show()

    def _rate_answer(self, is_correct: bool, difficulty: str):
        """
        评分

        Args:
            is_correct: 是否正确
            difficulty: 难度 ("easy", "normal", "hard")
        """
        if not self.current_entry:
            return

        try:
            # 提交复习结果
            success = self.review_service.submit_review(
                entry_id=self.current_entry.id,
                is_correct=is_correct,
                difficulty=difficulty
            )

            if success:
                if is_correct:
                    self.correct_count += 1

                # 更新进度
                self.progress_bar.setValue(self.current_index + 1)

                # 下一个
                self.current_index += 1
                self._show_next_entry()
            else:
                QMessageBox.warning(self, "警告", "提交复习结果失败，请重试")

        except Exception as e:
            logger.error(f"评分失败: {e}")
            QMessageBox.critical(self, "错误", f"评分失败: {e}")

    def _skip_current(self):
        """跳过当前词条"""
        self.current_index += 1
        self.progress_bar.setValue(self.current_index)
        self._show_next_entry()

    def _update_stats(self):
        """更新统计信息"""
        accuracy = (self.correct_count / self.current_index * 100) if self.current_index > 0 else 0
        self.stats_label.setText(
            f"进度: {self.current_index}/{self.total_count} | "
            f"正确率: {accuracy:.1f}% ({self.correct_count}/{self.current_index if self.current_index > 0 else 1})"
        )

    def _finish_review(self):
        """完成复习"""
        accuracy = (self.correct_count / self.total_count * 100) if self.total_count > 0 else 0

        QMessageBox.information(
            self,
            "复习完成",
            f"恭喜！本次复习已完成\n\n"
            f"复习数量: {self.total_count}\n"
            f"正确数量: {self.correct_count}\n"
            f"正确率: {accuracy:.1f}%\n\n"
            f"继续保持学习！"
        )

        self.review_completed.emit()
        self.close()

    def _quit_review(self):
        """退出复习"""
        if self.current_index < len(self.entries_to_review):
            reply = QMessageBox.question(
                self,
                "确认",
                f"当前还有 {len(self.entries_to_review) - self.current_index} 个词条未复习，\n确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        self.close()

    def keyPressEvent(self, event):
        """键盘事件"""
        key = event.key()

        if key == Qt.Key.Key_Space and not self.is_showing_answer:
            # 空格显示答案
            self._show_answer()
        elif self.is_showing_answer:
            # 数字键评分
            if key == Qt.Key.Key_1:
                self._rate_answer(False, "hard")
            elif key == Qt.Key.Key_2:
                self._rate_answer(True, "hard")
            elif key == Qt.Key.Key_3:
                self._rate_answer(True, "normal")
            elif key == Qt.Key.Key_4:
                self._rate_answer(True, "easy")
        elif key == Qt.Key.Key_Escape:
            # ESC退出
            self._quit_review()

        super().keyPressEvent(event)
