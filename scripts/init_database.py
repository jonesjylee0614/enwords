"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.data.database import db_manager
from src.utils.logger import setup_logger
# 导入所有模型（必须在create_all_tables之前导入）
from src.data.models import Entry, Tag, DailyStat, TranslationCache


def init_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 确保所有模型已导入
        logger.info(f"已加载模型: Entry, Tag, DailyStat, TranslationCache")
        
        # 创建所有表
        db_manager.create_all_tables()
        
        logger.success("数据库初始化完成!")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


if __name__ == "__main__":
    setup_logger()
    init_database()

