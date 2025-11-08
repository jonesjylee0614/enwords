"""
系统托盘图标
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject
from loguru import logger


class TrayIcon(QObject):
    """系统托盘图标"""
    
    # 信号
    show_main_window = pyqtSignal()
    quit_app = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.tray_icon = None
        self.init_tray()
    
    def init_tray(self):
        """初始化托盘图标"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon()
        
        # 设置图标（使用默认图标）
        # TODO: 替换为实际图标
        from PyQt6.QtWidgets import QApplication
        self.tray_icon.setIcon(QApplication.style().standardIcon(
            QApplication.style().StandardPixmap.SP_ComputerIcon
        ))
        
        # 设置提示文本
        self.tray_icon.setToolTip("TransLearn - 翻译学习工具")
        
        # 创建菜单
        menu = self._create_menu()
        self.tray_icon.setContextMenu(menu)
        
        # 双击事件
        self.tray_icon.activated.connect(self._on_activated)
        
        logger.debug("托盘图标初始化完成")
    
    def _create_menu(self) -> QMenu:
        """创建托盘菜单"""
        menu = QMenu()
        
        # 打开主窗口
        open_action = QAction("打开主窗口", menu)
        open_action.triggered.connect(self.show_main_window.emit)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)
        
        return menu
    
    def _on_activated(self, reason):
        """托盘图标激活事件"""
        try:
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                self.show_main_window.emit()
        except Exception as e:
            logger.error(f"托盘图标激活事件处理失败: {e}")
    
    def show(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
            logger.debug("托盘图标已显示")
    
    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()

