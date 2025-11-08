"""
语言检测
"""
import re
from typing import Optional
from loguru import logger

try:
    from langdetect import detect, DetectorFactory
    # 设置随机种子,确保结果可复现
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger.warning("langdetect 未安装,将使用简单规则检测")


class LanguageDetector:
    """语言检测器"""
    
    @staticmethod
    def detect(text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 待检测文本
            
        Returns:
            语言代码 (en/zh/ja等)
        """
        if not text:
            return "en"
        
        text = text.strip()
        
        # 优先使用简单规则(更快、更准确)
        rule_result = LanguageDetector._detect_by_rule(text)
        if rule_result:
            return rule_result
        
        # 使用 langdetect 库
        if LANGDETECT_AVAILABLE:
            try:
                lang = detect(text)
                logger.debug(f"语言检测结果: {lang}")
                return lang
            except Exception as e:
                logger.warning(f"语言检测失败: {e}")
        
        # 默认返回英语
        return "en"
    
    @staticmethod
    def _detect_by_rule(text: str) -> Optional[str]:
        """
        基于规则的语言检测
        
        Args:
            text: 待检测文本
            
        Returns:
            语言代码或None
        """
        # 中文检测
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) > len(text) * 0.3:
            return "zh"
        
        # 日文检测
        japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text)
        if len(japanese_chars) > 0:
            return "ja"
        
        # 韩文检测
        korean_chars = re.findall(r'[\uac00-\ud7af]', text)
        if len(korean_chars) > 0:
            return "ko"
        
        # 英文检测(包含字母)
        if re.search(r'[a-zA-Z]', text):
            return "en"
        
        return None
    
    @staticmethod
    def is_cjk(text: str) -> bool:
        """
        判断是否为中日韩文字
        
        Args:
            text: 待检测文本
            
        Returns:
            是否为CJK
        """
        cjk_chars = re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', text)
        return len(cjk_chars) > 0

