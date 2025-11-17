"""
在线词典翻译器
支持有道词典、金山词霸等在线词典API
"""
import hashlib
import time
import uuid
import httpx
from typing import Optional
from loguru import logger

from src.core.translator_interface import TranslatorInterface, TranslationResult
from src.utils.config_loader import config


class OnlineDictTranslator(TranslatorInterface):
    """在线词典翻译器"""

    def __init__(self):
        self.provider = config.translation.online_dict.provider if hasattr(config.translation, 'online_dict') else "youdao"
        self.api_key = config.translation.online_dict.api_key if hasattr(config.translation, 'online_dict') else ""
        self.timeout = config.translation.online_dict.timeout if hasattr(config.translation, 'online_dict') else 5

        if not self.api_key:
            logger.warning("在线词典 API Key 未配置")

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        使用在线词典翻译

        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译结果
        """
        try:
            if self.provider == "youdao":
                return await self._translate_youdao(text, source_lang, target_lang)
            elif self.provider == "iciba":
                return await self._translate_iciba(text, source_lang, target_lang)
            else:
                raise ValueError(f"不支持的在线词典提供商: {self.provider}")

        except Exception as e:
            logger.error(f"在线词典翻译失败: {e}")
            raise

    async def _translate_youdao(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        使用有道词典API翻译

        API文档: https://ai.youdao.com/DOCSIRMA/html/自然语言翻译/API文档/文本翻译服务/文本翻译服务-API文档.html
        """
        try:
            # 有道词典免费API（需要注册获取app_key和app_secret）
            # 这里使用的是有道智云的翻译API
            if not hasattr(config.translation.online_dict, 'app_key') or not hasattr(config.translation.online_dict, 'app_secret'):
                raise Exception("有道词典需要配置 app_key 和 app_secret")

            app_key = config.translation.online_dict.app_key
            app_secret = config.translation.online_dict.app_secret

            # 生成签名
            salt = str(uuid.uuid4())
            sign_str = app_key + text + salt + app_secret
            sign = hashlib.md5(sign_str.encode()).hexdigest()

            # 语言映射
            lang_map = {
                "en": "en",
                "zh": "zh-CHS",
                "ja": "ja",
                "ko": "ko"
            }

            from_lang = lang_map.get(source_lang, "auto")
            to_lang = lang_map.get(target_lang, "zh-CHS")

            # 构建请求
            url = "https://openapi.youdao.com/api"
            params = {
                "q": text,
                "from": from_lang,
                "to": to_lang,
                "appKey": app_key,
                "salt": salt,
                "sign": sign
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                data = response.json()

                # 检查响应
                if data.get("errorCode") == "0":
                    # 成功
                    translation = "\n".join(data.get("translation", []))

                    # 提取词典信息
                    explanation = None
                    pronunciation = None
                    examples = None

                    # 基本释义
                    if "basic" in data:
                        basic = data["basic"]
                        if "explains" in basic:
                            explanation = "\n".join(basic["explains"])
                        # 音标
                        if "phonetic" in basic:
                            pronunciation = basic["phonetic"]
                        elif "us-phonetic" in basic:
                            pronunciation = f"US: {basic['us-phonetic']}"
                        elif "uk-phonetic" in basic:
                            pronunciation = f"UK: {basic['uk-phonetic']}"

                    # 网络释义例句
                    if "web" in data:
                        web_examples = data["web"][:3]  # 最多3个
                        examples = [
                            f"{ex.get('key', '')}: {', '.join(ex.get('value', []))}"
                            for ex in web_examples
                        ]

                    return TranslationResult(
                        translation=translation,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        entry_type="word" if len(text.split()) <= 2 else "phrase",
                        explanation=explanation,
                        pronunciation=pronunciation,
                        examples=examples
                    )
                else:
                    error_msg = data.get("errorCode", "unknown")
                    raise Exception(f"有道API错误: {error_msg}")

        except Exception as e:
            logger.error(f"有道词典翻译失败: {e}")
            raise

    async def _translate_iciba(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        使用金山词霸API翻译

        金山词霸提供免费API: http://dict-co.iciba.com/api/dictionary.php
        """
        try:
            # 金山词霸免费API
            url = "http://dict-co.iciba.com/api/dictionary.php"
            params = {
                "w": text,
                "type": "json",
                "key": self.api_key if self.api_key else "your_key_here"  # 注册获取
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                data = response.json()

                # 解析结果
                if "symbols" in data and len(data["symbols"]) > 0:
                    symbol = data["symbols"][0]

                    # 音标
                    pronunciation = None
                    if "ph_am" in symbol:
                        pronunciation = f"US: {symbol['ph_am']}"
                    elif "ph_en" in symbol:
                        pronunciation = f"UK: {symbol['ph_en']}"

                    # 释义
                    parts = symbol.get("parts", [])
                    translations = []
                    for part in parts:
                        part_str = part.get("part", "")
                        means = part.get("means", [])
                        translations.append(f"{part_str} {', '.join(means)}")

                    translation = "\n".join(translations)
                    explanation = translation  # 金山词霸释义即翻译

                    return TranslationResult(
                        translation=translation,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        entry_type="word",
                        explanation=explanation,
                        pronunciation=pronunciation
                    )
                else:
                    # 无结果
                    raise KeyError(f"金山词霸未找到: {text}")

        except Exception as e:
            logger.error(f"金山词霸翻译失败: {e}")
            raise

    def get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成缓存键"""
        import hashlib
        key_str = f"online_dict:{self.provider}:{text.lower()}:{source_lang}:{target_lang}"
        return hashlib.md5(key_str.encode()).hexdigest()
