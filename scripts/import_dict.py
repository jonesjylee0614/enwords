"""
词典导入工具
从各种格式导入词典数据
"""
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger


def create_sample_dict():
    """创建示例词典数据"""
    sample_data = {
        "hello": {
            "translation": "你好",
            "pronunciation": "həˈləʊ",
            "explanation": "用于打招呼或引起注意",
            "examples": [
                "Hello, how are you?",
                "Say hello to your mother for me."
            ]
        },
        "world": {
            "translation": "世界",
            "pronunciation": "wɜːld",
            "explanation": "地球；世界；领域",
            "examples": [
                "Hello world!",
                "Travel around the world."
            ]
        },
        "translate": {
            "translation": "翻译",
            "pronunciation": "trænsˈleɪt",
            "explanation": "把...译成另一种语言",
            "examples": [
                "Can you translate this for me?",
                "The book has been translated into Chinese."
            ]
        },
        "dictionary": {
            "translation": "词典；字典",
            "pronunciation": "ˈdɪkʃəneri",
            "explanation": "按字母顺序列出单词及其释义的工具书",
            "examples": [
                "Look it up in the dictionary.",
                "An English dictionary."
            ]
        },
        "language": {
            "translation": "语言",
            "pronunciation": "ˈlæŋɡwɪdʒ",
            "explanation": "人类用来交流的系统",
            "examples": [
                "Learn a new language.",
                "Body language."
            ]
        },
        "learn": {
            "translation": "学习；学会",
            "pronunciation": "lɜːn",
            "explanation": "获得知识或技能",
            "examples": [
                "Learn English.",
                "Never too old to learn."
            ]
        },
        "study": {
            "translation": "学习；研究",
            "pronunciation": "ˈstʌdi",
            "explanation": "花时间学习或研究某事物",
            "examples": [
                "Study hard.",
                "Case study."
            ]
        },
        "word": {
            "translation": "单词；词",
            "pronunciation": "wɜːd",
            "explanation": "语言的最小单位",
            "examples": [
                "What's the word for...?",
                "In other words."
            ]
        },
        "sentence": {
            "translation": "句子",
            "pronunciation": "ˈsentəns",
            "explanation": "表达完整意思的一组词",
            "examples": [
                "Write a sentence.",
                "Complete the sentence."
            ]
        },
        "text": {
            "translation": "文本；正文",
            "pronunciation": "tekst",
            "explanation": "书面或印刷的文字",
            "examples": [
                "Read the text.",
                "Text message."
            ]
        },
        "computer": {
            "translation": "计算机；电脑",
            "pronunciation": "kəmˈpjuːtə",
            "explanation": "电子计算设备",
            "examples": [
                "Use a computer.",
                "Computer science."
            ]
        },
        "program": {
            "translation": "程序；节目",
            "pronunciation": "ˈprəʊɡræm",
            "explanation": "计算机指令集合",
            "examples": [
                "Computer program.",
                "TV program."
            ]
        },
        "software": {
            "translation": "软件",
            "pronunciation": "ˈsɒftweə",
            "explanation": "计算机程序的集合",
            "examples": [
                "Install software.",
                "Software development."
            ]
        },
        "application": {
            "translation": "应用；应用程序",
            "pronunciation": "ˌæplɪˈkeɪʃn",
            "explanation": "为特定目的设计的程序",
            "examples": [
                "Mobile application.",
                "Job application."
            ]
        },
        "window": {
            "translation": "窗口；窗户",
            "pronunciation": "ˈwɪndəʊ",
            "explanation": "窗户；界面窗口",
            "examples": [
                "Open the window.",
                "Application window."
            ]
        },
        "file": {
            "translation": "文件",
            "pronunciation": "faɪl",
            "explanation": "计算机存储的数据集合",
            "examples": [
                "Save the file.",
                "File manager."
            ]
        },
        "search": {
            "translation": "搜索；查找",
            "pronunciation": "sɜːtʃ",
            "explanation": "寻找某物",
            "examples": [
                "Search the web.",
                "Search engine."
            ]
        },
        "find": {
            "translation": "找到；发现",
            "pronunciation": "faɪnd",
            "explanation": "发现或获得",
            "examples": [
                "Find the answer.",
                "Find and replace."
            ]
        },
        "save": {
            "translation": "保存；储蓄",
            "pronunciation": "seɪv",
            "explanation": "保存数据或金钱",
            "examples": [
                "Save the document.",
                "Save money."
            ]
        },
        "delete": {
            "translation": "删除",
            "pronunciation": "dɪˈliːt",
            "explanation": "移除或消除",
            "examples": [
                "Delete the file.",
                "Press delete key."
            ]
        }
    }
    
    return sample_data


def import_from_json(input_file: Path, output_file: Path):
    """
    从JSON文件导入词典
    
    Args:
        input_file: 输入JSON文件路径
        output_file: 输出词典文件路径
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 保存到输出文件
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"导入完成，共 {len(data)} 个词条")
        logger.info(f"词典保存到: {output_file}")
    
    except Exception as e:
        logger.error(f"导入失败: {e}")


def main():
    """主函数"""
    logger.info("词典导入工具")
    
    # 输出路径
    dict_dir = project_root / "data" / "dict"
    dict_dir.mkdir(parents=True, exist_ok=True)
    output_file = dict_dir / "en-zh.json"
    
    # 检查是否已存在
    if output_file.exists():
        logger.warning(f"词典文件已存在: {output_file}")
        response = input("是否覆盖? (y/n): ")
        if response.lower() != 'y':
            logger.info("取消导入")
            return
    
    # 创建示例词典
    logger.info("创建示例词典...")
    sample_data = create_sample_dict()
    
    # 保存
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    logger.success(f"词典创建完成！")
    logger.info(f"路径: {output_file}")
    logger.info(f"词条数: {len(sample_data)}")
    
    print("\n" + "="*60)
    print("词典示例（前5个）:")
    print("="*60)
    for i, (word, entry) in enumerate(list(sample_data.items())[:5]):
        print(f"{i+1}. {word} - {entry['translation']}")
        print(f"   音标: {entry.get('pronunciation', 'N/A')}")
        print(f"   例句: {entry.get('examples', ['N/A'])[0]}")
        print()


if __name__ == "__main__":
    main()

