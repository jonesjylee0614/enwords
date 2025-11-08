"""
OCR 文字识别提取器
"""
from typing import Optional
from loguru import logger

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger.warning("PaddleOCR 未安装，OCR功能不可用")


class OCRExtractor:
    """OCR 文字提取器"""
    
    def __init__(self):
        self.ocr = None
        if PADDLEOCR_AVAILABLE:
            try:
                # 初始化PaddleOCR
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang="ch",  # 支持中英文
                    use_gpu=False,
                    show_log=False
                )
                logger.info("PaddleOCR 初始化成功")
            except Exception as e:
                logger.error(f"PaddleOCR 初始化失败: {e}")
        else:
            logger.warning("PaddleOCR 未安装，请运行: pip install paddleocr")
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """
        从图片中提取文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            提取的文本，或 None
        """
        if not self.ocr:
            logger.error("OCR 未初始化")
            return None
        
        try:
            # 执行OCR识别
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                logger.warning("未识别到文字")
                return None
            
            # 提取文本
            texts = []
            for line in result[0]:
                text = line[1][0]  # 提取文本内容
                texts.append(text)
            
            # 合并文本
            full_text = "\n".join(texts)
            logger.debug(f"OCR识别成功: {full_text[:50]}...")
            
            return full_text
        
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """检查OCR是否可用"""
        return self.ocr is not None

