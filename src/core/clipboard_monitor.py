"""
剪贴板监听器
"""
import time
import pyperclip
from threading import Thread
from PyQt6.QtCore import QObject, pyqtSignal
from loguru import logger

from src.utils.config_loader import config
from src.core.text_extractor import TextExtractor


class ClipboardMonitor(QObject):
    """剪贴板监听器"""
    
    # 信号：检测到文本变化
    text_copied = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._is_monitoring = False
        self._last_text = ""
        self._monitor_thread = None
    
    @property
    def is_monitoring(self) -> bool:
        """是否正在监听"""
        return self._is_monitoring
    
    def start(self):
        """启动监听"""
        if self._is_monitoring:
            logger.warning("剪贴板监听已经在运行")
            return
        
        self._is_monitoring = True
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("剪贴板监听已启动")
    
    def stop(self):
        """停止监听"""
        self._is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
        logger.info("剪贴板监听已停止")
    
    def _monitor_loop(self):
        """监听循环"""
        delay = config.features.clipboard_delay / 1000.0  # 转换为秒
        
        while self._is_monitoring:
            try:
                # 获取剪贴板内容
                current_text = pyperclip.paste()
                
                # 检查是否变化
                if current_text != self._last_text:
                    self._last_text = current_text
                    
                    # 应用延迟（避免误触）
                    if delay > 0:
                        time.sleep(delay)
                    
                    # 验证文本
                    if self._should_process(current_text):
                        logger.debug(f"检测到剪贴板变化: {current_text[:50]}...")
                        self.text_copied.emit(current_text.strip())
                
                # 休眠
                time.sleep(0.2)
            
            except Exception as e:
                logger.error(f"剪贴板监听错误: {e}")
                time.sleep(1)
    
    def _should_process(self, text: str) -> bool:
        """
        判断是否应该处理该文本
        
        Args:
            text: 剪贴板文本
            
        Returns:
            是否处理
        """
        if not text:
            return False
        
        text = text.strip()
        
        # 基本验证
        if not TextExtractor.validate_text(text):
            return False
        
        # 过滤重复内容
        if config.features.clipboard_filter_duplicates:
            if text == self._last_text:
                return False
        
        # 长度限制
        if len(text) > 1000:
            logger.debug("文本过长，跳过")
            return False
        
        return True

