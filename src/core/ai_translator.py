"""
AI 翻译器
"""
import json
import asyncio
from typing import Optional
from loguru import logger

from src.core.translator_interface import TranslatorInterface, TranslationResult
from src.utils.config_loader import config


class AITranslator(TranslatorInterface):
    """AI 翻译器（支持 OpenAI / DashScope）"""
    
    def __init__(self):
        self.provider = config.translation.ai.provider
        self.model = config.translation.ai.model
        self.api_key = config.translation.ai.api_key
        self.timeout = config.translation.ai.timeout
        
        if not self.api_key:
            logger.warning("AI API Key 未配置")
    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        使用 AI 翻译
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译结果
        """
        try:
            if self.provider == "openai":
                return await self._translate_openai(text, source_lang, target_lang)
            elif self.provider == "dashscope":
                return await self._translate_dashscope(text, source_lang, target_lang)
            else:
                raise ValueError(f"不支持的 AI 提供商: {self.provider}")
        
        except Exception as e:
            logger.error(f"AI 翻译失败: {e}")
            # 返回错误信息
            return TranslationResult(
                translation=f"翻译失败: {str(e)}",
                source_lang=source_lang,
                target_lang=target_lang
            )
    
    async def _translate_openai(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """使用 OpenAI API 翻译"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=config.translation.ai.base_url or None
            )
            
            # 构建提示词
            prompt = self._build_prompt(text, source_lang, target_lang)
            
            # 调用 API
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的翻译助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=config.translation.ai.temperature,
                    max_tokens=config.translation.ai.max_tokens,
                ),
                timeout=self.timeout
            )
            
            # 解析结果
            content = response.choices[0].message.content
            return self._parse_response(content, source_lang, target_lang)
        
        except Exception as e:
            logger.error(f"OpenAI 翻译失败: {e}")
            raise
    
    async def _translate_dashscope(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """使用 DashScope API 翻译"""
        try:
            import dashscope
            from dashscope import Generation
            
            dashscope.api_key = self.api_key
            
            # 构建提示词
            prompt = self._build_prompt(text, source_lang, target_lang)
            
            # 调用 API
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    Generation.call,
                    model=self.model,
                    prompt=prompt,
                    temperature=config.translation.ai.temperature,
                    max_tokens=config.translation.ai.max_tokens,
                ),
                timeout=self.timeout
            )
            
            # 解析结果
            if response.status_code == 200:
                content = response.output.text
                return self._parse_response(content, source_lang, target_lang)
            else:
                raise Exception(f"API 错误: {response.message}")
        
        except Exception as e:
            logger.error(f"DashScope 翻译失败: {e}")
            raise
    
    def _build_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """构建提示词"""
        lang_map = {
            "en": "英语",
            "zh": "中文",
            "ja": "日语",
            "ko": "韩语"
        }
        
        source_name = lang_map.get(source_lang, source_lang)
        target_name = lang_map.get(target_lang, target_lang)
        
        prompt = f"""请将以下{source_name}文本翻译成{target_name}，要求：
1. 准确传达原意
2. 符合{target_name}表达习惯
3. 保持原文的语气和风格

原文：
{text}

请直接返回翻译结果，无需其他说明。"""
        
        return prompt
    
    def _parse_response(
        self,
        content: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """解析 AI 响应"""
        try:
            # 尝试解析 JSON 格式
            data = json.loads(content)
            return TranslationResult(
                translation=data.get("translation", content),
                source_lang=source_lang,
                target_lang=target_lang,
                explanation=data.get("explanation"),
                domain=data.get("domain"),
            )
        except json.JSONDecodeError:
            # 普通文本格式
            return TranslationResult(
                translation=content.strip(),
                source_lang=source_lang,
                target_lang=target_lang,
            )
    
    def get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成缓存键"""
        import hashlib
        key_str = f"{self.provider}:{self.model}:{text}:{source_lang}:{target_lang}"
        return hashlib.md5(key_str.encode()).hexdigest()

