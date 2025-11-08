"""
热键测试脚本
用于诊断热键功能是否正常
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.utils.logger import setup_logger
from src.core.hotkey_manager import HotkeyManager


def test_hotkey_callback():
    """测试回调函数"""
    print("\n" + "="*50)
    print("✅ 热键被成功触发！")
    print("="*50 + "\n")
    logger.info("热键回调函数被调用")


def main():
    """主函数"""
    setup_logger()
    
    print("\n" + "="*70)
    print("  TransLearn 热键测试工具")
    print("="*70)
    print("\n📌 说明：")
    print("  1. 本脚本用于测试热键功能是否正常")
    print("  2. 按 Ctrl+Q 测试热键是否响应")
    print("  3. 按 Ctrl+C 退出程序")
    print("\n")
    
    # 创建热键管理器
    hotkey_manager = HotkeyManager()
    
    # 注册测试热键
    try:
        hotkey_manager.register("ctrl+q", test_hotkey_callback)
        logger.info("已注册测试热键: Ctrl+Q")
        print("✅ 热键已注册: Ctrl+Q")
    except Exception as e:
        logger.error(f"注册热键失败: {e}")
        print(f"❌ 注册热键失败: {e}")
        return
    
    # 启动监听
    try:
        hotkey_manager.start()
        logger.info("热键监听已启动")
        print("✅ 热键监听已启动")
        print("\n⌨️  请按 Ctrl+Q 测试...")
        print("   按 Ctrl+C 退出\n")
    except Exception as e:
        logger.error(f"启动热键监听失败: {e}")
        print(f"❌ 启动热键监听失败: {e}")
        return
    
    # 保持运行
    try:
        import threading
        event = threading.Event()
        event.wait()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        hotkey_manager.stop()


if __name__ == "__main__":
    main()

