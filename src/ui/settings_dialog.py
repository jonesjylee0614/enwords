"""
设置对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QSpinBox, QDoubleSpinBox, QListWidget,
    QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from loguru import logger

from src.utils.config_loader import config
import toml
from pathlib import Path


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(700, 600)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tabs = QTabWidget()
        tabs.addTab(self._create_general_tab(), "通用")
        tabs.addTab(self._create_hotkey_tab(), "热键")
        tabs.addTab(self._create_translation_tab(), "翻译")
        tabs.addTab(self._create_appearance_tab(), "外观")
        tabs.addTab(self._create_blacklist_tab(), "黑名单")
        tabs.addTab(self._create_about_tab(), "关于")
        
        layout.addWidget(tabs)
        
        # 底部按钮
        buttons = self._create_buttons()
        layout.addWidget(buttons)
    
    def _create_general_tab(self) -> QWidget:
        """创建通用设置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 语言
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        layout.addRow("界面语言:", self.language_combo)
        
        # 开机启动
        self.autostart_check = QCheckBox("开机自动启动")
        layout.addRow("", self.autostart_check)
        
        # 剪贴板监听
        self.clipboard_monitor_check = QCheckBox("启用剪贴板监听")
        layout.addRow("", self.clipboard_monitor_check)
        
        # 剪贴板延迟
        self.clipboard_delay_spin = QSpinBox()
        self.clipboard_delay_spin.setRange(0, 2000)
        self.clipboard_delay_spin.setSuffix(" ms")
        layout.addRow("剪贴板延迟:", self.clipboard_delay_spin)
        
        layout.addStretch()
        return widget
    
    def _create_hotkey_tab(self) -> QWidget:
        """创建热键设置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 翻译热键
        self.translate_hotkey = QLineEdit()
        self.translate_hotkey.setPlaceholderText("例如: ctrl+q")
        layout.addRow("翻译快捷键:", self.translate_hotkey)
        
        # OCR热键
        self.ocr_hotkey = QLineEdit()
        self.ocr_hotkey.setPlaceholderText("例如: ctrl+shift+q")
        layout.addRow("OCR截图:", self.ocr_hotkey)
        
        # 切换监听热键
        self.toggle_hotkey = QLineEdit()
        self.toggle_hotkey.setPlaceholderText("例如: ctrl+shift+t")
        layout.addRow("切换监听:", self.toggle_hotkey)
        
        # 打开主窗口热键
        self.main_window_hotkey = QLineEdit()
        self.main_window_hotkey.setPlaceholderText("例如: ctrl+shift+l")
        layout.addRow("打开主窗口:", self.main_window_hotkey)
        
        # 提示
        tip = QLabel("注意：修改热键后需要重启应用才能生效")
        tip.setStyleSheet("color: #f59e0b; font-size: 12px;")
        layout.addRow("", tip)
        
        layout.addStretch()
        return widget
    
    def _create_translation_tab(self) -> QWidget:
        """创建翻译设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI翻译设置
        ai_group = QGroupBox("AI 翻译")
        ai_layout = QFormLayout(ai_group)
        
        # 提供商
        self.ai_provider_combo = QComboBox()
        self.ai_provider_combo.addItems(["dashscope", "openai", "ollama"])
        ai_layout.addRow("提供商:", self.ai_provider_combo)
        
        # 模型
        self.ai_model_edit = QLineEdit()
        ai_layout.addRow("模型:", self.ai_model_edit)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        ai_layout.addRow("API Key:", self.api_key_edit)
        
        # 超时
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 60)
        self.timeout_spin.setSuffix(" 秒")
        ai_layout.addRow("超时:", self.timeout_spin)
        
        layout.addWidget(ai_group)
        
        # 翻译选项
        options_group = QGroupBox("翻译选项")
        options_layout = QVBoxLayout(options_group)
        
        self.auto_detect_lang_check = QCheckBox("自动检测语言")
        options_layout.addWidget(self.auto_detect_lang_check)
        
        self.force_ai_check = QCheckBox("强制使用 AI 翻译")
        options_layout.addWidget(self.force_ai_check)
        
        self.auto_save_check = QCheckBox("自动保存到词库")
        options_layout.addWidget(self.auto_save_check)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        return widget
    
    def _create_appearance_tab(self) -> QWidget:
        """创建外观设置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 主题
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["自动", "明亮", "暗色"])
        layout.addRow("主题:", self.theme_combo)
        
        # 悬浮窗宽度
        self.popup_width_spin = QSpinBox()
        self.popup_width_spin.setRange(300, 800)
        self.popup_width_spin.setSuffix(" px")
        layout.addRow("悬浮窗宽度:", self.popup_width_spin)
        
        # 悬浮窗透明度
        self.popup_opacity_spin = QDoubleSpinBox()
        self.popup_opacity_spin.setRange(0.5, 1.0)
        self.popup_opacity_spin.setSingleStep(0.05)
        layout.addRow("悬浮窗透明度:", self.popup_opacity_spin)
        
        # 显示动画
        self.show_animation_check = QCheckBox("启用显示动画")
        layout.addRow("", self.show_animation_check)
        
        layout.addStretch()
        return widget
    
    def _create_blacklist_tab(self) -> QWidget:
        """创建黑名单设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("在这些应用中不会触发翻译:")
        layout.addWidget(label)
        
        # 黑名单列表
        self.blacklist_widget = QListWidget()
        layout.addWidget(self.blacklist_widget)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self._add_blacklist)
        buttons_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("删除")
        remove_btn.clicked.connect(self._remove_blacklist)
        buttons_layout.addWidget(remove_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return widget
    
    def _create_about_tab(self) -> QWidget:
        """创建关于标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 应用名称
        name_label = QLabel("TransLearn")
        name_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3b82f6;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 版本
        version_label = QLabel(f"版本 {config.app.version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 描述
        desc_label = QLabel("Windows 个人翻译学习工具")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # 功能特性
        features = QLabel(
            "✨ 即时翻译\n"
            "🧠 智能引擎\n"
            "📚 个人词库\n"
            "🔄 科学复习\n"
            "🔒 隐私优先"
        )
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)
        
        layout.addSpacing(20)
        
        # 版权
        copyright_label = QLabel("© 2025 TransLearn Team\nMIT License")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        return widget
    
    def _create_buttons(self) -> QWidget:
        """创建底部按钮"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        layout.addStretch()
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        layout.addWidget(save_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #e5e7eb;
                color: #374151;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #d1d5db;
            }
        """)
        layout.addWidget(cancel_btn)
        
        return widget
    
    def load_settings(self):
        """加载设置"""
        try:
            # 通用
            self.language_combo.setCurrentIndex(0)
            self.clipboard_monitor_check.setChecked(config.features.clipboard_monitor)
            self.clipboard_delay_spin.setValue(config.features.clipboard_delay)
            
            # 热键
            self.translate_hotkey.setText(config.hotkey.translate)
            self.ocr_hotkey.setText(config.hotkey.screenshot_ocr)
            self.toggle_hotkey.setText(config.hotkey.toggle_monitor)
            self.main_window_hotkey.setText(config.hotkey.open_main_window)
            
            # 翻译
            provider_index = ["dashscope", "openai", "ollama"].index(config.translation.ai.provider)
            self.ai_provider_combo.setCurrentIndex(provider_index)
            self.ai_model_edit.setText(config.translation.ai.model)
            self.api_key_edit.setText(config.translation.ai.api_key)
            self.timeout_spin.setValue(config.translation.ai.timeout)
            
            self.auto_detect_lang_check.setChecked(config.translation.auto_detect_language)
            self.force_ai_check.setChecked(config.translation.force_ai)
            self.auto_save_check.setChecked(config.features.auto_save)
            
            # 外观
            theme_index = ["auto", "light", "dark"].index(config.app.theme)
            self.theme_combo.setCurrentIndex(theme_index)
            self.popup_width_spin.setValue(config.ui.popup.width)
            self.popup_opacity_spin.setValue(config.ui.popup.opacity)
            self.show_animation_check.setChecked(config.ui.popup.show_animation)
            
            # 黑名单
            self.blacklist_widget.clear()
            self.blacklist_widget.addItems(config.blacklist.apps)
            
            logger.debug("设置加载完成")
        
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 读取配置文件
            config_path = Path(__file__).parent.parent.parent / "data" / "config.toml"
            
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = toml.load(f)
            
            # 更新配置
            # 通用
            config_dict["features"]["clipboard_monitor"] = self.clipboard_monitor_check.isChecked()
            config_dict["features"]["clipboard_delay"] = self.clipboard_delay_spin.value()
            
            # 热键
            config_dict["hotkey"]["translate"] = self.translate_hotkey.text()
            config_dict["hotkey"]["screenshot_ocr"] = self.ocr_hotkey.text()
            config_dict["hotkey"]["toggle_monitor"] = self.toggle_hotkey.text()
            config_dict["hotkey"]["open_main_window"] = self.main_window_hotkey.text()
            
            # 翻译
            config_dict["translation"]["ai"]["provider"] = self.ai_provider_combo.currentText()
            config_dict["translation"]["ai"]["model"] = self.ai_model_edit.text()
            config_dict["translation"]["ai"]["api_key"] = self.api_key_edit.text()
            config_dict["translation"]["ai"]["timeout"] = self.timeout_spin.value()
            
            config_dict["translation"]["auto_detect_language"] = self.auto_detect_lang_check.isChecked()
            config_dict["translation"]["force_ai"] = self.force_ai_check.isChecked()
            config_dict["features"]["auto_save"] = self.auto_save_check.isChecked()
            
            # 外观
            theme_map = {0: "auto", 1: "light", 2: "dark"}
            config_dict["app"]["theme"] = theme_map[self.theme_combo.currentIndex()]
            config_dict["ui"]["popup"]["width"] = self.popup_width_spin.value()
            config_dict["ui"]["popup"]["opacity"] = self.popup_opacity_spin.value()
            config_dict["ui"]["popup"]["show_animation"] = self.show_animation_check.isChecked()
            
            # 黑名单
            blacklist = [self.blacklist_widget.item(i).text() for i in range(self.blacklist_widget.count())]
            config_dict["blacklist"]["apps"] = blacklist
            
            # 保存到文件
            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(config_dict, f)
            
            QMessageBox.information(self, "成功", "设置已保存！\n某些设置需要重启应用后生效。")
            self.accept()
            logger.info("设置保存成功")
        
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败:\n{str(e)}")
    
    def _add_blacklist(self):
        """添加黑名单"""
        from PyQt6.QtWidgets import QInputDialog
        
        app_name, ok = QInputDialog.getText(self, "添加黑名单", "应用名称:")
        if ok and app_name:
            self.blacklist_widget.addItem(app_name)
    
    def _remove_blacklist(self):
        """删除黑名单"""
        current_item = self.blacklist_widget.currentItem()
        if current_item:
            self.blacklist_widget.takeItem(self.blacklist_widget.row(current_item))

