"""
智能路由器 - 选择合适的翻译器
"""
import re
from loguru import logger

from src.core.translator_interface import TranslatorType
from src.core.language_detector import LanguageDetector
from src.utils.config_loader import config


class SmartRouter:
    """智能翻译路由器"""
    
    def __init__(self):
        self.detector = LanguageDetector()
    
    async def detect_language(self, text: str) -> str:
        """
        检测语言
        
        Args:
            text: 待检测文本
            
        Returns:
            语言代码
        """
        return self.detector.detect(text)
    
    def choose_translator(self, text: str, source_lang: str) -> TranslatorType:
        """
        智能选择翻译器
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            
        Returns:
            翻译器类型
        """
        # 1. 用户强制模式
        if config.translation.force_ai:
            logger.debug("强制使用 AI 翻译")
            return TranslatorType.AI
        
        # 2. 判断文本类型
        text_type = self._classify_text(text)
        
        # 3. 根据文本类型选择翻译器
        if text_type == "word":
            # 单词 → 本地词典 → 在线词典
            if config.translation.local_dict.enabled:
                logger.debug("单词,使用本地词典")
                return TranslatorType.LOCAL_DICT
            else:
                logger.debug("单词,使用在线词典")
                return TranslatorType.ONLINE_DICT
        
        elif text_type == "phrase":
            # 短语 → 在线词典
            logger.debug("短语,使用在线词典")
            return TranslatorType.ONLINE_DICT
        
        else:
            # 句子/段落 → AI 翻译
            logger.debug("句子/段落,使用 AI 翻译")
            return TranslatorType.AI
    
    def _classify_text(self, text: str) -> str:
        """
        分类文本类型
        
        Args:
            text: 文本
            
        Returns:
            类型: word/phrase/sentence/paragraph
        """
        text = text.strip()
        
        # 统计词数
        word_count = self._count_words(text)
        
        # 判断
        if word_count <= config.translation.word_threshold:
            return "word"
        elif word_count <= config.translation.phrase_threshold:
            return "phrase"
        elif len(text) < 200:
            return "sentence"
        else:
            return "paragraph"
    
    def _count_words(self, text: str) -> int:
        """
        统计词数
        
        Args:
            text: 文本
            
        Returns:
            词数
        """
        # 中日韩文字：按字符数
        if LanguageDetector.is_cjk(text):
            cjk_chars = re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', text)
            return len(cjk_chars)
        
        # 英文等：按空格分隔的词数
        words = re.findall(r'\b\w+\b', text)
        return len(words)

