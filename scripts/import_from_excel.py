"""
从 Excel 文件导入词库到本地词典和数据库

支持的 Excel 格式：
1. 列 A: 英文单词
2. 列 B: 中文翻译
3. 列 C: 词性（可选）
4. 列 D: 音标（可选）
5. 列 E: 例句（可选）
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from loguru import logger

from src.utils.config_loader import config
from src.data.database import DatabaseManager
from src.data.models import Entry
from src.data.repository import EntryRepository


class ExcelDictImporter:
    """Excel 词库导入器"""
    
    def __init__(self):
        self.dict_file = project_root / "data" / "dict" / "en-zh.json"
        self.db_manager = None
        self.entry_repo = None
        
    def import_from_excel(self, excel_path: str, update_local_dict: bool = True, 
                          save_to_db: bool = True, start_row: int = 0, 
                          max_rows: int = None):
        """
        从 Excel 文件导入词库
        
        Args:
            excel_path: Excel 文件路径
            update_local_dict: 是否更新本地词典 JSON 文件
            save_to_db: 是否保存到数据库
            start_row: 起始行（0-based，默认从第一行开始）
            max_rows: 最多导入多少行（None 表示全部导入）
        """
        logger.info(f"开始导入 Excel 词库: {excel_path}")
        
        # 1. 读取 Excel 文件
        try:
            df = pd.read_excel(excel_path, header=0)
            logger.info(f"Excel 文件读取成功，共 {len(df)} 行")
        except Exception as e:
            logger.error(f"读取 Excel 文件失败: {e}")
            return False
        
        # 2. 检查必需的列
        required_columns = ['word', 'translation']
        if not all(col in df.columns for col in required_columns):
            # 尝试使用列索引
            logger.warning("未找到标准列名，尝试使用列索引...")
            if len(df.columns) < 2:
                logger.error(f"Excel 文件至少需要 2 列（英文单词、中文翻译）")
                return False
            
            # 使用前两列
            df.columns = ['word', 'translation'] + list(df.columns[2:])
            logger.info(f"使用列索引: 第1列=单词, 第2列=翻译")
        
        # 添加可选列（如果不存在则创建）
        if 'pos' not in df.columns:
            df['pos'] = ''
        if 'pronunciation' not in df.columns:
            df['pronunciation'] = ''
        if 'example' not in df.columns:
            df['example'] = ''
        
        # 3. 过滤和清理数据
        # 删除空行
        df = df.dropna(subset=['word', 'translation'])
        
        # 删除重复的单词（保留第一个）
        df = df.drop_duplicates(subset=['word'], keep='first')
        
        # 清理文本（去除前后空格）
        df['word'] = df['word'].str.strip()
        df['translation'] = df['translation'].str.strip()
        df['pos'] = df['pos'].fillna('').str.strip()
        df['pronunciation'] = df['pronunciation'].fillna('').str.strip()
        df['example'] = df['example'].fillna('').str.strip()
        
        # 应用行限制
        if start_row > 0:
            df = df.iloc[start_row:]
            logger.info(f"从第 {start_row + 1} 行开始导入")
        
        if max_rows is not None:
            df = df.head(max_rows)
            logger.info(f"最多导入 {max_rows} 行")
        
        logger.info(f"有效词条: {len(df)} 个")
        
        # 4. 转换为字典格式
        dict_data = {}
        for _, row in df.iterrows():
            word = row['word'].lower()  # 统一转为小写
            entry = {
                "translation": row['translation']
            }
            
            if row['pos']:
                entry['pos'] = row['pos']
            if row['pronunciation']:
                entry['pronunciation'] = row['pronunciation']
            if row['example']:
                entry['example'] = row['example']
            
            dict_data[word] = entry
        
        # 5. 更新本地词典
        if update_local_dict:
            success = self._update_local_dict(dict_data)
            if not success:
                return False
        
        # 6. 保存到数据库
        if save_to_db:
            success = self._save_to_db(dict_data)
            if not success:
                return False
        
        logger.success(f"导入完成！共导入 {len(dict_data)} 个词条")
        return True
    
    def _update_local_dict(self, dict_data: dict) -> bool:
        """更新本地词典 JSON 文件"""
        try:
            # 读取现有词典
            existing_dict = {}
            if self.dict_file.exists():
                with open(self.dict_file, 'r', encoding='utf-8') as f:
                    existing_dict = json.load(f)
                logger.info(f"现有词典: {len(existing_dict)} 个词条")
            
            # 合并（新词条会覆盖旧词条）
            existing_dict.update(dict_data)
            
            # 保存
            self.dict_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.dict_file, 'w', encoding='utf-8') as f:
                json.dump(existing_dict, f, ensure_ascii=False, indent=2)
            
            logger.success(f"本地词典已更新: {self.dict_file}")
            logger.info(f"总词条数: {len(existing_dict)}")
            return True
        
        except Exception as e:
            logger.error(f"更新本地词典失败: {e}")
            return False
    
    def _save_to_db(self, dict_data: dict) -> bool:
        """保存到数据库"""
        try:
            # 初始化数据库
            self.db_manager = DatabaseManager()
            self.db_manager.create_all_tables()
            self.entry_repo = EntryRepository()
            
            logger.info(f"开始保存到数据库...")
            
            saved_count = 0
            skipped_count = 0
            error_count = 0
            
            for word, entry_data in dict_data.items():
                try:
                    # 检查是否已存在
                    existing = self.entry_repo.get_by_text(word)
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # 创建词条
                    entry = Entry(
                        source_text=word,
                        translation=entry_data['translation'],
                        source_lang='en',
                        target_lang='zh',
                        notes=entry_data.get('example', ''),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    # 保存
                    self.entry_repo.save(entry)
                    saved_count += 1
                    
                    # 每 100 条打印一次进度
                    if saved_count % 100 == 0:
                        logger.info(f"已保存 {saved_count} 条...")
                
                except Exception as e:
                    error_count += 1
                    logger.warning(f"保存词条失败 '{word}': {e}")
                    if error_count > 10:  # 如果错误太多，提前终止
                        logger.error("错误过多，终止导入")
                        return False
            
            logger.success(f"数据库保存完成！")
            logger.info(f"  - 新增: {saved_count} 条")
            logger.info(f"  - 跳过（已存在）: {skipped_count} 条")
            logger.info(f"  - 失败: {error_count} 条")
            
            return True
        
        except Exception as e:
            logger.error(f"保存到数据库失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="从 Excel 文件导入词库")
    parser.add_argument("excel_file", help="Excel 文件路径")
    parser.add_argument("--no-local", action="store_true", help="不更新本地词典")
    parser.add_argument("--no-db", action="store_true", help="不保存到数据库")
    parser.add_argument("--start", type=int, default=0, help="起始行（0-based）")
    parser.add_argument("--max", type=int, help="最多导入多少行")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    excel_path = Path(args.excel_file)
    if not excel_path.exists():
        logger.error(f"文件不存在: {excel_path}")
        return
    
    # 执行导入
    importer = ExcelDictImporter()
    success = importer.import_from_excel(
        str(excel_path),
        update_local_dict=not args.no_local,
        save_to_db=not args.no_db,
        start_row=args.start,
        max_rows=args.max
    )
    
    if success:
        logger.success("🎉 导入成功！")
    else:
        logger.error("❌ 导入失败！")


if __name__ == "__main__":
    main()

