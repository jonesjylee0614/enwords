"""
最简单的热键测试
"""
from pynput import keyboard

print("\n" + "="*70)
print("  最简单的热键测试")
print("="*70)
print("\n说明：")
print("  1. 本脚本测试 pynput 能否检测组合键")
print("  2. 请按 Ctrl+5 测试")
print("  3. 按 ESC 退出")
print("\n")

# 当前按下的键
current_keys = set()

def on_press(key):
    """按键按下"""
    try:
        # 添加到当前按键集合
        current_keys.add(key)
        
        # 检查是否按下 Ctrl+5
        if (keyboard.Key.ctrl_l in current_keys or keyboard.Key.ctrl in current_keys):
            if hasattr(key, 'char') and key.char == '5':
                print("\n" + "="*70)
                print("  ✅ 检测到 Ctrl+5！")
                print("="*70 + "\n")
        
        # 打印所有按键
        print(f"按下: {key}")
        
    except Exception as e:
        print(f"错误: {e}")

def on_release(key):
    """按键释放"""
    try:
        # 从集合中移除
        if key in current_keys:
            current_keys.remove(key)
        
        # ESC 退出
        if key == keyboard.Key.esc:
            print("\n程序退出\n")
            return False
            
    except Exception as e:
        print(f"错误: {e}")

print("开始监听...\n")

# 启动监听
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

