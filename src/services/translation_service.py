"""
翻译服务（门面模式）
"""
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from src.core.translator_interface import TranslationResult, TranslatorType
from src.core.translator_factory import TranslatorFactory
from src.core.smart_router import SmartRouter
from src.data.repository import EntryRepository, CacheRepository, StatsRepository
from src.data.models import Entry, TranslationCache
from src.utils.config_loader import config


class TranslationService:
    """翻译服务门面"""
    
    def __init__(self):
        self.factory = TranslatorFactory()
        self.router = SmartRouter()
        self.entry_repo = EntryRepository()
        self.cache_repo = CacheRepository()
        self.stats_repo = StatsRepository()
    
    async def translate(
        self,
        text: str,
        source_lang: Optional[str] = None,
        target_lang: str = "zh",
        save_to_db: bool = False,
        context: Optional[dict] = None
    ) -> TranslationResult:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言（None=自动检测）
            target_lang: 目标语言
            save_to_db: 是否保存到数据库
            context: 上下文信息（来源、URL等）
        
        Returns:
            翻译结果
        """
        try:
            # 1. 参数验证
            text = text.strip()
            if not text:
                raise ValueError("文本不能为空")
            
            # 2. 语言检测
            if not source_lang:
                source_lang = await self.router.detect_language(text)
            
            # 3. 检查缓存
            if config.cache.enabled:
                cache_key = self._generate_cache_key(text, source_lang, target_lang)
                cached = self.cache_repo.get(cache_key)
                if cached:
                    logger.info(f"命中缓存: {text[:20]}...")
                    return TranslationResult(
                        translation=cached.translation,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        translator_type=cached.translator_type
                    )
            
            # 4. 智能路由选择翻译器
            translator_type = self.router.choose_translator(text, source_lang)
            
            logger.info(f"使用翻译器: {translator_type.value} | 文本: {text[:30]}...")
            
            # 5. 执行翻译
            start_time = asyncio.get_event_loop().time()
            
            # 使用工厂获取翻译器
            translator = self.factory.get_translator(translator_type)
            
            try:
                result = await translator.translate(text, source_lang, target_lang)
            except KeyError as e:
                # 本地词典未找到，降级到 AI
                if translator_type == TranslatorType.LOCAL_DICT:
                    logger.info(f"本地词典未找到 '{text}'，尝试 AI 翻译")
                    
                    # 检查是否配置了AI
                    if not config.translation.ai.api_key:
                        # 没有配置AI，返回友好提示
                        return TranslationResult(
                            translation=f"❌ 本地词典未收录「{text}」\n\n💡 提示：配置 AI 翻译可获得更多内容\n编辑 data/config.toml 添加 API key",
                            source_lang=source_lang,
                            target_lang=target_lang,
                            translator_type="local_dict_not_found"
                        )
                    
                    translator = self.factory.get_translator(TranslatorType.AI)
                    try:
                        result = await translator.translate(text, source_lang, target_lang)
                        result.translator_type = "ai_fallback"
                    except Exception as ai_error:
                        logger.error(f"AI翻译失败: {ai_error}")
                        return TranslationResult(
                            translation=f"❌ 翻译失败\n\n本地词典未收录「{text}」\nAI 翻译也失败了：{str(ai_error)[:100]}",
                            source_lang=source_lang,
                            target_lang=target_lang,
                            translator_type="failed"
                        )
                else:
                    raise
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            result.translator_type = translator_type.value
            result.translation_time = elapsed
            
            # 6. 缓存结果
            if config.cache.enabled:
                self._save_to_cache(cache_key, text, result)
            
            # 7. 保存到数据库
            if save_to_db or self._should_auto_save(text):
                self._save_entry(text, result, context)
            
            # 8. 更新统计
            self._update_stats(translator_type)
            
            logger.success(f"翻译完成，耗时 {elapsed:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            raise
    
    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成缓存键"""
        key_str = f"{text}:{source_lang}:{target_lang}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _save_to_cache(self, cache_key: str, text: str, result: TranslationResult):
        """保存到缓存"""
        try:
            expire_days = config.cache.expire_days
            expires_at = datetime.now() + timedelta(days=expire_days)
            
            cache = TranslationCache(
                cache_key=cache_key,
                source_text=text,
                translation=result.translation,
                translator_type=result.translator_type or "unknown",
                expires_at=expires_at
            )
            
            self.cache_repo.set(cache)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def _should_auto_save(self, text: str) -> bool:
        """判断是否应该自动保存"""
        if not config.features.auto_save:
            return False
        
        # 查询历史次数
        try:
            count = self.entry_repo.get_query_count(text)
            return count >= config.features.auto_save_threshold
        except Exception as e:
            logger.error(f"查询次数失败: {e}")
            return False
    
    def _save_entry(self, text: str, result: TranslationResult, context: Optional[dict]):
        """保存词条"""
        try:
            entry = Entry(
                source_text=text,
                translation=result.translation,
                source_lang=result.source_lang,
                target_lang=result.target_lang,
                entry_type=result.entry_type,
                translator_type=result.translator_type,
                translation_time=result.translation_time,
                context=context.get('text') if context else None,
                source_app=context.get('app') if context else None,
                source_url=context.get('url') if context else None,
            )
            
            self.entry_repo.save(entry)
            logger.debug("词条已保存")
        except Exception as e:
            logger.error(f"保存词条失败: {e}")
    
    def _update_stats(self, translator_type: TranslatorType):
        """更新统计"""
        try:
            stats_data = {"translation_count": 1}
            
            if translator_type == TranslatorType.AI:
                stats_data["ai_calls"] = 1
            
            self.stats_repo.update_today_stats(**stats_data)
        except Exception as e:
            logger.error(f"更新统计失败: {e}")

