"""
翻译器工厂
"""
from typing import Dict
from loguru import logger

from src.core.translator_interface import TranslatorInterface, TranslatorType
from src.core.local_dict_translator import LocalDictTranslator
from src.core.ai_translator import AITranslator
from src.core.online_dict_translator import OnlineDictTranslator


class TranslatorFactory:
    """翻译器工厂"""
    
    _instances: Dict[TranslatorType, TranslatorInterface] = {}
    
    @classmethod
    def get_translator(cls, translator_type: TranslatorType) -> TranslatorInterface:
        """
        获取翻译器实例（单例模式）
        
        Args:
            translator_type: 翻译器类型
        
        Returns:
            翻译器实例
        """
        # 检查是否已创建
        if translator_type in cls._instances:
            return cls._instances[translator_type]
        
        # 创建新实例
        if translator_type == TranslatorType.LOCAL_DICT:
            instance = LocalDictTranslator()
        elif translator_type == TranslatorType.AI:
            instance = AITranslator()
        elif translator_type == TranslatorType.ONLINE_DICT:
            instance = OnlineDictTranslator()
        else:
            raise ValueError(f"未知的翻译器类型: {translator_type}")
        
        # 缓存实例
        cls._instances[translator_type] = instance
        logger.debug(f"创建翻译器: {translator_type.value}")
        
        return instance

