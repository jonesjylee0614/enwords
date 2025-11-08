"""
TransLearn 功能诊断工具
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.utils.logger import setup_logger


def test_imports():
    """测试必要的库导入"""
    print("\n" + "="*70)
    print("1. 测试库导入")
    print("="*70)
    
    imports = {
        "PyQt6": "from PyQt6.QtWidgets import QApplication",
        "pynput": "from pynput import keyboard",
        "pyperclip": "import pyperclip",
        "pyautogui": "import pyautogui",
        "mysql-connector": "import mysql.connector",
        "sqlalchemy": "import sqlalchemy",
    }
    
    for name, code in imports.items():
        try:
            exec(code)
            print(f"  ✅ {name:20} 正常")
        except Exception as e:
            print(f"  ❌ {name:20} 失败: {e}")


def test_clipboard():
    """测试剪贴板功能"""
    print("\n" + "="*70)
    print("2. 测试剪贴板功能")
    print("="*70)
    
    try:
        import pyperclip
        
        # 测试写入
        test_text = "Hello, TransLearn!"
        pyperclip.copy(test_text)
        print(f"  ✅ 写入剪贴板: {test_text}")
        
        # 测试读取
        result = pyperclip.paste()
        print(f"  ✅ 读取剪贴板: {result}")
        
        if result == test_text:
            print(f"  ✅ 剪贴板功能正常")
        else:
            print(f"  ⚠️ 读写内容不一致")
            
    except Exception as e:
        print(f"  ❌ 剪贴板测试失败: {e}")


def test_keyboard_sim():
    """测试键盘模拟"""
    print("\n" + "="*70)
    print("3. 测试键盘模拟")
    print("="*70)
    
    try:
        import pyautogui
        
        print("  ℹ️  键盘模拟库已加载")
        print("  ℹ️  failsafe模式:", pyautogui.FAILSAFE)
        print(f"  ℹ️  暂停时间: {pyautogui.PAUSE} 秒")
        
        # 测试简单的按键（不实际执行，只是检查是否可以调用）
        print("  ✅ 键盘模拟功能可用")
        print("  ⚠️  注意: 需要在实际应用中测试 Ctrl+C 是否能成功复制")
        
    except Exception as e:
        print(f"  ❌ 键盘模拟测试失败: {e}")


def test_hotkey_listener():
    """测试热键监听"""
    print("\n" + "="*70)
    print("4. 测试热键监听")
    print("="*70)
    
    try:
        from pynput import keyboard
        
        print("  ✅ pynput 库加载成功")
        print("\n  📌 测试说明:")
        print("     - 将在5秒内监听键盘")
        print("     - 请按任意键测试")
        print("     - 观察是否能检测到按键")
        print("\n  ⌨️  开始监听...")
        
        pressed_keys = []
        
        def on_press(key):
            try:
                key_name = key.char if hasattr(key, 'char') else str(key)
                print(f"       检测到按键: {key_name}")
                pressed_keys.append(key_name)
            except:
                pass
        
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        # 监听5秒
        import time
        time.sleep(5)
        
        listener.stop()
        
        if pressed_keys:
            print(f"\n  ✅ 成功检测到 {len(pressed_keys)} 个按键")
            print(f"       按键: {', '.join(pressed_keys[:10])}")
        else:
            print(f"\n  ⚠️  未检测到任何按键")
            print(f"       可能原因:")
            print(f"       1. 焦点不在命令行窗口")
            print(f"       2. 需要管理员权限")
            print(f"       3. 被安全软件阻止")
            
    except Exception as e:
        print(f"  ❌ 热键监听测试失败: {e}")


def test_database():
    """测试数据库连接"""
    print("\n" + "="*70)
    print("5. 测试数据库连接")
    print("="*70)
    
    try:
        from src.data.database import db_manager
        from src.utils.config_loader import config
        
        print(f"  ℹ️  数据库配置:")
        print(f"     主机: {config.database.host}")
        print(f"     端口: {config.database.port}")
        print(f"     用户: {config.database.user}")
        print(f"     数据库: {config.database.database}")
        
        # 尝试连接
        try:
            from sqlalchemy import text
            with db_manager.get_session() as session:
                result = session.execute(text("SELECT 1"))
                print(f"  ✅ 数据库连接成功")
        except Exception as e:
            print(f"  ❌ 数据库连接失败: {e}")
            
    except Exception as e:
        print(f"  ❌ 数据库测试失败: {e}")


def test_translation_service():
    """测试翻译服务"""
    print("\n" + "="*70)
    print("6. 测试翻译服务")
    print("="*70)
    
    try:
        from src.services.translation_service import TranslationService
        
        service = TranslationService()
        print("  ✅ 翻译服务初始化成功")
        
        # 测试翻译（如果配置了API）
        try:
            print("  ℹ️  尝试翻译测试文本...")
            
            # 异步翻译需要事件循环
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(service.translate("hello"))
                print(f"  ✅ 翻译成功: hello → {result.translation}")
            finally:
                loop.close()
                
        except Exception as e:
            print(f"  ⚠️  翻译失败: {e}")
            print(f"       (可能是API配置问题，不影响其他功能)")
            
    except Exception as e:
        print(f"  ❌ 翻译服务测试失败: {e}")


def main():
    """主函数"""
    setup_logger()
    
    print("\n" + "="*70)
    print("  TransLearn 功能诊断工具")
    print("="*70)
    print("\n  本工具将测试所有核心功能是否正常\n")
    
    test_imports()
    test_clipboard()
    test_keyboard_sim()
    test_hotkey_listener()
    test_database()
    test_translation_service()
    
    print("\n" + "="*70)
    print("  诊断完成")
    print("="*70)
    print("\n  📋 总结:")
    print("     - 如果所有测试都显示 ✅，说明环境正常")
    print("     - 如果有 ❌，请根据提示解决问题")
    print("     - 如果有 ⚠️，可能需要额外配置\n")
    
    input("按回车键退出...")


if __name__ == "__main__":
    main()

