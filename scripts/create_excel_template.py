"""
创建 Excel 词库模板

生成一个示例 Excel 文件，包含正确的格式和一些示例词条
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from loguru import logger


def create_template():
    """创建 Excel 模板"""
    
    # 示例数据
    data = {
        'word': [
            'apple', 'banana', 'computer', 'program', 'translate',
            'beautiful', 'happy', 'study', 'work', 'life',
            'morning', 'evening', 'today', 'tomorrow', 'yesterday',
            'friend', 'family', 'school', 'teacher', 'student'
        ],
        'translation': [
            '苹果', '香蕉', '计算机', '程序', '翻译',
            '美丽的', '快乐的', '学习', '工作', '生活',
            '早晨', '傍晚', '今天', '明天', '昨天',
            '朋友', '家庭', '学校', '老师', '学生'
        ],
        'pos': [
            'n.', 'n.', 'n.', 'n.', 'v.',
            'adj.', 'adj.', 'v./n.', 'v./n.', 'n./v.',
            'n.', 'n.', 'n./adv.', 'n./adv.', 'n./adv.',
            'n.', 'n.', 'n.', 'n.', 'n.'
        ],
        'pronunciation': [
            '/ˈæpl/', '/bəˈnænə/', '/kəmˈpjuːtər/', '/ˈproʊɡræm/', '/trænsˈleɪt/',
            '/ˈbjuːtɪfl/', '/ˈhæpi/', '/ˈstʌdi/', '/wɜːrk/', '/laɪf/',
            '/ˈmɔːrnɪŋ/', '/ˈiːvnɪŋ/', '/təˈdeɪ/', '/təˈmɑːroʊ/', '/ˈjestərdeɪ/',
            '/frend/', '/ˈfæməli/', '/skuːl/', '/ˈtiːtʃər/', '/ˈstuːdnt/'
        ],
        'example': [
            'I eat an apple every day.',
            'Bananas are yellow.',
            'I need a new computer.',
            'This is a good program.',
            'Can you translate this?',
            'She is beautiful.',
            'I am happy today.',
            'I study English every day.',
            'I work in a company.',
            'Life is wonderful.',
            'Good morning!',
            'Good evening!',
            'Today is Monday.',
            'Tomorrow will be better.',
            'Yesterday was Sunday.',
            'He is my best friend.',
            'I love my family.',
            'I go to school by bus.',
            'My teacher is kind.',
            'She is a good student.'
        ]
    }
    
    # 创建 DataFrame
    df = pd.DataFrame(data)
    
    # 保存为 Excel
    output_file = project_root / "data" / "dict_template.xlsx"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    logger.success(f"Excel 模板已创建: {output_file}")
    logger.info(f"包含 {len(df)} 个示例词条")
    logger.info("\n你可以：")
    logger.info("  1. 打开这个文件，编辑或添加更多词条")
    logger.info("  2. 或者用这个格式创建自己的词库")
    logger.info("  3. 然后运行：python scripts/import_from_excel.py data/dict_template.xlsx")


if __name__ == "__main__":
    create_template()

