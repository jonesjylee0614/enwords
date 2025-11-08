"""
测试系统托盘图标
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction
from loguru import logger
from src.utils.logger import setup_logger


def main():
    """主函数"""
    setup_logger()
    
    print("\n" + "="*70)
    print("  TransLearn 托盘图标测试工具")
    print("="*70)
    print("\n📌 说明：")
    print("  1. 本脚本测试系统托盘图标是否正常显示")
    print("  2. 查看任务栏右下角是否有图标")
    print("  3. 右键点击图标测试菜单")
    print("  4. 按 Ctrl+C 退出")
    print("\n")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建托盘图标
    tray = QSystemTrayIcon()
    tray.setIcon(app.style().standardIcon(
        app.style().StandardPixmap.SP_ComputerIcon
    ))
    tray.setToolTip("TransLearn 测试")
    
    # 创建菜单
    menu = QMenu()
    
    test_action = QAction("测试菜单项", menu)
    test_action.triggered.connect(lambda: print("\n✅ 菜单项被点击！"))
    menu.addAction(test_action)
    
    menu.addSeparator()
    
    quit_action = QAction("退出", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    
    tray.setContextMenu(menu)
    
    # 双击事件
    tray.activated.connect(lambda reason: print(f"\n🖱️ 托盘图标被点击: {reason}"))
    
    # 显示托盘图标
    tray.show()
    
    print("✅ 托盘图标已创建并显示")
    print("\n📍 请在任务栏右下角查找图标")
    print("   (可能需要点击 ^ 展开隐藏的图标)\n")
    print("⌨️  按 Ctrl+C 或右键菜单选择'退出'来关闭\n")
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

