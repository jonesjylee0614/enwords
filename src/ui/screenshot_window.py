"""
截图选择窗口
"""
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QScreen
from loguru import logger


class ScreenshotWindow(QWidget):
    """截图选择窗口"""
    
    # 信号：选区确定
    region_selected = pyqtSignal(QRect)
    
    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        self.screenshot = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        # 无边框全屏窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())
        
        # 设置光标
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def start_capture(self):
        """开始截图"""
        try:
            # 获取屏幕截图
            screen = QApplication.primaryScreen()
            self.screenshot = screen.grabWindow(0)
            
            # 显示窗口
            self.showFullScreen()
            logger.debug("截图窗口已显示")
        
        except Exception as e:
            logger.error(f"开始截图失败: {e}")
    
    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.is_selecting = True
    
    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()  # 重绘
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.end_pos = event.pos()
            self.is_selecting = False
            
            # 计算选区
            if self.start_pos and self.end_pos:
                x1, y1 = self.start_pos.x(), self.start_pos.y()
                x2, y2 = self.end_pos.x(), self.end_pos.y()
                
                # 确保 x1 < x2, y1 < y2
                x = min(x1, x2)
                y = min(y1, y2)
                w = abs(x2 - x1)
                h = abs(y2 - y1)
                
                if w > 10 and h > 10:  # 最小尺寸
                    region = QRect(x, y, w, h)
                    
                    # 发射信号
                    self.region_selected.emit(region)
                    logger.debug(f"选区: {region}")
            
            # 关闭窗口
            self.close()
    
    def keyPressEvent(self, event):
        """按键事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        
        # 绘制背景（半透明）
        if self.screenshot:
            painter.drawPixmap(0, 0, self.screenshot)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # 绘制选区
        if self.start_pos and self.end_pos:
            x1, y1 = self.start_pos.x(), self.start_pos.y()
            x2, y2 = self.end_pos.x(), self.end_pos.y()
            
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            # 清除选区的半透明遮罩
            if self.screenshot:
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                painter.fillRect(x, y, w, h, Qt.GlobalColor.transparent)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                
                # 绘制选区内容
                painter.drawPixmap(x, y, self.screenshot.copy(x, y, w, h))
            
            # 绘制选区边框
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(x, y, w, h)

