"""
发音服务 (TTS)
"""
import asyncio
import tempfile
from pathlib import Path
from typing import Optional
from loguru import logger

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts 未安装，发音功能不可用")


class PronunciationService:
    """发音服务"""
    
    # 语言到语音的映射
    VOICE_MAP = {
        "en": "en-US-AriaNeural",
        "zh": "zh-CN-XiaoxiaoNeural",
        "ja": "ja-JP-NanamiNeural",
        "ko": "ko-KR-SunHiNeural",
    }
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "translearn_audio"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def pronounce(self, text: str, lang: str = "en") -> bool:
        """
        发音
        
        Args:
            text: 要发音的文本
            lang: 语言代码
            
        Returns:
            是否成功
        """
        if not EDGE_TTS_AVAILABLE:
            logger.error("edge-tts 未安装")
            return False
        
        try:
            # 获取语音
            voice = self.VOICE_MAP.get(lang, self.VOICE_MAP["en"])
            
            # 生成临时文件
            audio_file = self.temp_dir / f"temp_{hash(text)}.mp3"
            
            # 生成音频
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(audio_file))
            
            # 播放音频
            await self._play_audio(audio_file)
            
            # 删除临时文件
            try:
                audio_file.unlink()
            except:
                pass
            
            logger.debug(f"发音完成: {text[:20]}...")
            return True
        
        except Exception as e:
            logger.error(f"发音失败: {e}")
            return False
    
    async def _play_audio(self, audio_file: Path):
        """播放音频文件"""
        try:
            import platform
            
            system = platform.system()
            
            if system == "Windows":
                # Windows 使用 winsound
                import winsound
                winsound.PlaySound(str(audio_file), winsound.SND_FILENAME)
            elif system == "Darwin":
                # macOS 使用 afplay
                import subprocess
                subprocess.run(["afplay", str(audio_file)], check=True)
            else:
                # Linux 使用 mpg123 或 ffplay
                import subprocess
                try:
                    subprocess.run(["mpg123", str(audio_file)], check=True)
                except FileNotFoundError:
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", str(audio_file)], check=True)
        
        except Exception as e:
            logger.error(f"播放音频失败: {e}")
            raise

