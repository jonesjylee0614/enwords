"""
文本提取器（取词功能）
"""
import time
import pyperclip
import pyautogui
from loguru import logger


class TextExtractor:
    """文本提取器"""
    
    @staticmethod
    def extract_selected_text() -> str:
        """
        提取当前选中的文本（不污染剪贴板）
        
        采用"三明治法":
        1. 备份剪贴板
        2. 模拟 Ctrl+C
        3. 获取新内容
        4. 恢复剪贴板
        
        Returns:
            选中的文本
        """
        try:
            # 1. 备份剪贴板
            old_clipboard = ""
            try:
                old_clipboard = pyperclip.paste()
            except Exception as e:
                logger.warning(f"备份剪贴板失败: {e}")
            
            # 2. 清空剪贴板（避免误判）
            pyperclip.copy("")
            time.sleep(0.05)
            
            # 3. 模拟复制
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)  # 等待系统响应（增加等待时间）
            
            # 4. 获取新内容
            new_text = ""
            try:
                new_text = pyperclip.paste()
                logger.debug(f"从剪贴板获取: '{new_text[:50] if new_text else '(空)'}'")
            except Exception as e:
                logger.error(f"获取剪贴板内容失败: {e}")
            
            # 5. 恢复剪贴板
            try:
                pyperclip.copy(old_clipboard)
            except Exception as e:
                logger.warning(f"恢复剪贴板失败: {e}")
            
            # 6. 返回结果
            # 即使新内容和旧内容相同，如果不是空的，也返回（可能是重复复制）
            if new_text:
                text = new_text.strip()
                if text:
                    logger.info(f"提取文本成功: {text[:50]}...")
                    return text
            
            logger.warning(f"未提取到文本 - old: '{old_clipboard[:30] if old_clipboard else '(空)'}', new: '{new_text[:30] if new_text else '(空)'}'")
            return ""
        
        except Exception as e:
            logger.error(f"文本提取失败: {e}")
            return ""
    
    @staticmethod
    def validate_text(text: str) -> bool:
        """
        验证文本是否有效
        
        Args:
            text: 待验证的文本
            
        Returns:
            是否有效
        """
        if not text:
            return False
        
        text = text.strip()
        
        # 长度检查
        if len(text) < 1 or len(text) > 5000:
            return False
        
        # 过滤纯数字
        if text.isdigit():
            return False
        
        # 过滤文件路径
        if text.startswith(('C:\\', 'D:\\', '/', '\\\\')) or ':\\' in text:
            return False
        
        # 过滤URL（可选）
        if text.startswith(('http://', 'https://', 'ftp://')):
            return False
        
        return True

