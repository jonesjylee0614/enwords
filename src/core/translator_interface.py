"""
翻译器接口定义
"""
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class TranslatorType(Enum):
    """翻译器类型"""
    LOCAL_DICT = "local_dict"
    ONLINE_DICT = "online_dict"
    AI = "ai"


@dataclass
class TranslationResult:
    """翻译结果"""
    # 基本信息
    translation: str
    source_lang: str = "en"
    target_lang: str = "zh"
    entry_type: str = "sentence"  # word/phrase/sentence/paragraph
    
    # 扩展信息
    explanation: Optional[str] = None  # 补充说明
    pronunciation: Optional[str] = None  # 发音
    examples: Optional[list] = None  # 例句
    domain: Optional[str] = None  # 领域
    
    # 元数据
    translator_type: Optional[str] = None
    translation_time: Optional[float] = None
    
    def __str__(self):
        return self.translation


class TranslatorInterface(ABC):
    """翻译器接口"""
    
    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译结果
        """
        pass
    
    @abstractmethod
    def get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        生成缓存键
        
        Args:
            text: 文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            缓存键
        """
        pass

