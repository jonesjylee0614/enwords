"""
词条详情与编辑对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QGroupBox,
    QFormLayout, QMessageBox, QListWidget, QInputDialog,
    QWidget
)
from PyQt6.QtCore import Qt
from loguru import logger

from src.data.models import Entry
from src.data.repository import EntryRepository


class EntryDetailDialog(QDialog):
    """词条详情对话框"""
    
    def __init__(self, entry: Entry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.entry_repo = EntryRepository()
        
        self.setWindowTitle("词条详情")
        self.resize(600, 700)
        self.init_ui()
        self.load_entry()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 基本信息
        basic_group = self._create_basic_group()
        layout.addWidget(basic_group)
        
        # 翻译信息
        translation_group = self._create_translation_group()
        layout.addWidget(translation_group)
        
        # 学习数据
        learning_group = self._create_learning_group()
        layout.addWidget(learning_group)
        
        # 标签
        tags_group = self._create_tags_group()
        layout.addWidget(tags_group)
        
        # 笔记
        notes_group = self._create_notes_group()
        layout.addWidget(notes_group)
        
        # 底部按钮
        buttons = self._create_buttons()
        layout.addWidget(buttons)
    
    def _create_basic_group(self) -> QGroupBox:
        """创建基本信息组"""
        group = QGroupBox("基本信息")
        layout = QFormLayout(group)
        
        # 原文
        self.source_edit = QTextEdit()
        self.source_edit.setMaximumHeight(80)
        layout.addRow("原文:", self.source_edit)
        
        # 翻译
        self.translation_edit = QTextEdit()
        self.translation_edit.setMaximumHeight(80)
        layout.addRow("翻译:", self.translation_edit)
        
        # 类型
        self.type_label = QLabel()
        layout.addRow("类型:", self.type_label)
        
        # 语言对
        self.lang_label = QLabel()
        layout.addRow("语言:", self.lang_label)
        
        return group
    
    def _create_translation_group(self) -> QGroupBox:
        """创建翻译信息组"""
        group = QGroupBox("翻译信息")
        layout = QFormLayout(group)
        
        # 翻译器类型
        self.translator_label = QLabel()
        layout.addRow("翻译器:", self.translator_label)
        
        # 翻译耗时
        self.time_label = QLabel()
        layout.addRow("耗时:", self.time_label)
        
        # 创建时间
        self.created_label = QLabel()
        layout.addRow("创建时间:", self.created_label)
        
        return group
    
    def _create_learning_group(self) -> QGroupBox:
        """创建学习数据组"""
        group = QGroupBox("学习数据")
        layout = QFormLayout(group)
        
        # 熟悉度
        self.familiarity_label = QLabel()
        layout.addRow("熟悉度:", self.familiarity_label)
        
        # 复习次数
        self.review_count_label = QLabel()
        layout.addRow("复习次数:", self.review_count_label)
        
        # 上次复习
        self.last_review_label = QLabel()
        layout.addRow("上次复习:", self.last_review_label)
        
        return group
    
    def _create_tags_group(self) -> QGroupBox:
        """创建标签组"""
        group = QGroupBox("标签")
        layout = QVBoxLayout(group)
        
        # 标签列表
        self.tags_list = QListWidget()
        self.tags_list.setMaximumHeight(100)
        layout.addWidget(self.tags_list)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        
        add_tag_btn = QPushButton("添加标签")
        add_tag_btn.clicked.connect(self._add_tag)
        buttons_layout.addWidget(add_tag_btn)
        
        remove_tag_btn = QPushButton("删除标签")
        remove_tag_btn.clicked.connect(self._remove_tag)
        buttons_layout.addWidget(remove_tag_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return group
    
    def _create_notes_group(self) -> QGroupBox:
        """创建笔记组"""
        group = QGroupBox("笔记")
        layout = QVBoxLayout(group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("在这里添加个人笔记...")
        layout.addWidget(self.notes_edit)
        
        return group
    
    def _create_buttons(self) -> QWidget:
        """创建按钮"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self._delete_entry)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        layout.addWidget(delete_btn)
        
        layout.addStretch()
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_entry)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        layout.addWidget(save_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #e5e7eb;
                color: #374151;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #d1d5db;
            }
        """)
        layout.addWidget(close_btn)
        
        return widget
    
    def load_entry(self):
        """加载词条数据"""
        try:
            # 基本信息
            self.source_edit.setPlainText(self.entry.source_text)
            self.translation_edit.setPlainText(self.entry.translation)
            self.type_label.setText(self.entry.entry_type or "未知")
            self.lang_label.setText(f"{self.entry.source_lang} → {self.entry.target_lang}")
            
            # 翻译信息
            self.translator_label.setText(self.entry.translator_type or "未知")
            if self.entry.translation_time:
                self.time_label.setText(f"{self.entry.translation_time:.2f} 秒")
            else:
                self.time_label.setText("N/A")
            
            if self.entry.created_at:
                self.created_label.setText(self.entry.created_at.strftime("%Y-%m-%d %H:%M"))
            else:
                self.created_label.setText("N/A")
            
            # 学习数据
            self.familiarity_label.setText(f"{self.entry.familiarity}/5")
            self.review_count_label.setText(str(self.entry.review_count or 0))
            if self.entry.last_review:
                self.last_review_label.setText(self.entry.last_review.strftime("%Y-%m-%d %H:%M"))
            else:
                self.last_review_label.setText("从未复习")
            
            # 标签
            if self.entry.tags:
                import json
                try:
                    tags = json.loads(self.entry.tags)
                    self.tags_list.addItems(tags)
                except:
                    pass
            
            # 笔记
            if self.entry.notes:
                self.notes_edit.setPlainText(self.entry.notes)
            
            logger.debug(f"词条数据加载完成: {self.entry.id}")
        
        except Exception as e:
            logger.error(f"加载词条失败: {e}")
    
    def _save_entry(self):
        """保存词条"""
        try:
            # 更新词条数据
            self.entry.source_text = self.source_edit.toPlainText()
            self.entry.translation = self.translation_edit.toPlainText()
            
            # 更新标签
            import json
            tags = [self.tags_list.item(i).text() for i in range(self.tags_list.count())]
            self.entry.tags = json.dumps(tags, ensure_ascii=False) if tags else None
            
            # 更新笔记
            self.entry.notes = self.notes_edit.toPlainText() or None
            
            # 保存到数据库
            self.entry_repo.save(self.entry)
            
            QMessageBox.information(self, "成功", "词条已保存！")
            self.accept()
            logger.info(f"词条保存成功: {self.entry.id}")
        
        except Exception as e:
            logger.error(f"保存词条失败: {e}")
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")
    
    def _delete_entry(self):
        """删除词条"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个词条吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.entry_repo.delete(self.entry.id)
                QMessageBox.information(self, "成功", "词条已删除！")
                self.accept()
                logger.info(f"词条删除成功: {self.entry.id}")
            except Exception as e:
                logger.error(f"删除词条失败: {e}")
                QMessageBox.critical(self, "错误", f"删除失败:\n{str(e)}")
    
    def _add_tag(self):
        """添加标签"""
        tag, ok = QInputDialog.getText(self, "添加标签", "标签名称:")
        if ok and tag:
            self.tags_list.addItem(tag)
    
    def _remove_tag(self):
        """删除标签"""
        current_item = self.tags_list.currentItem()
        if current_item:
            self.tags_list.takeItem(self.tags_list.row(current_item))

