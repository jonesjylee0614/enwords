"""
本地词典翻译器
"""
import json
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger

from src.core.translator_interface import TranslatorInterface, TranslationResult


class LocalDictTranslator(TranslatorInterface):
    """本地词典翻译器（离线查询）"""
    
    def __init__(self):
        self.dict_data: Dict[str, dict] = {}
        self.dict_loaded = False
        self._load_dictionary()
    
    def _load_dictionary(self):
        """加载词典数据"""
        try:
            # 词典文件路径
            dict_path = Path(__file__).parent.parent.parent / "data" / "dict" / "en-zh.json"
            
            if not dict_path.exists():
                logger.warning(f"词典文件不存在: {dict_path}")
                return
            
            # 加载JSON数据
            with open(dict_path, "r", encoding="utf-8") as f:
                self.dict_data = json.load(f)
            
            self.dict_loaded = True
            logger.info(f"本地词典加载完成，共 {len(self.dict_data)} 个词条")
        
        except Exception as e:
            logger.error(f"加载词典失败: {e}")
    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        使用本地词典翻译
        
        Args:
            text: 待翻译文本（单词）
            source_lang: 源语言
            target_lang: 目标语言
        
        Returns:
            翻译结果
        """
        # 规范化文本（转小写，去空格）
        word = text.strip().lower()
        
        # 查询词典
        entry = self.dict_data.get(word)
        
        if entry:
            # 找到翻译
            translation = entry.get("translation", "")
            explanation = entry.get("explanation")
            pronunciation = entry.get("pronunciation")
            examples = entry.get("examples", [])
            
            logger.debug(f"本地词典查询成功: {word} → {translation}")
            
            return TranslationResult(
                translation=translation,
                source_lang=source_lang,
                target_lang=target_lang,
                entry_type="word",
                explanation=explanation,
                pronunciation=pronunciation,
                examples=examples
            )
        else:
            # 未找到翻译
            logger.debug(f"本地词典未找到: {word}")
            raise KeyError(f"词典中未找到: {word}")
    
    def get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成缓存键"""
        import hashlib
        key_str = f"local_dict:{text.lower()}:{source_lang}:{target_lang}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def exists(self, word: str) -> bool:
        """
        检查词典中是否存在该单词
        
        Args:
            word: 单词
        
        Returns:
            是否存在
        """
        word = word.strip().lower()
        return word in self.dict_data
    
    def search(self, keyword: str, limit: int = 20) -> List[str]:
        """
        搜索词典
        
        Args:
            keyword: 关键词
            limit: 返回数量限制
        
        Returns:
            匹配的单词列表
        """
        keyword = keyword.lower()
        results = []
        
        for word in self.dict_data.keys():
            if keyword in word:
                results.append(word)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_word_count(self) -> int:
        """获取词典词数"""
        return len(self.dict_data)

