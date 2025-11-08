"""
全局热键管理器
"""
from typing import Callable, Dict, Set
from pynput import keyboard
from loguru import logger


class HotkeyManager:
    """全局热键管理器"""
    
    def __init__(self):
        self.listener: keyboard.Listener = None
        self.callbacks: Dict[frozenset, Callable] = {}
        self._current_keys: Set[str] = set()
        self._triggered_hotkeys: Set[frozenset] = set()  # 已触发的热键集合
        self._last_trigger_time: Dict[frozenset, float] = {}  # 最后触发时间
        self._debounce_interval = 0.5  # 防抖间隔（秒）
        self._is_running = False
    
    def register(self, hotkey: str, callback: Callable):
        """
        注册热键
        
        Args:
            hotkey: 热键字符串，如 "ctrl+q"
            callback: 回调函数
        """
        keys = self._parse_hotkey(hotkey)
        self.callbacks[frozenset(keys)] = callback
        logger.info(f"注册热键: {hotkey}")
    
    def unregister(self, hotkey: str):
        """注销热键"""
        keys = self._parse_hotkey(hotkey)
        key_set = frozenset(keys)
        if key_set in self.callbacks:
            del self.callbacks[key_set]
            logger.info(f"注销热键: {hotkey}")
    
    def start(self):
        """启动监听"""
        if self._is_running:
            logger.warning("热键监听已经在运行")
            return
        
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        self._is_running = True
        logger.info("热键监听已启动")
    
    def stop(self):
        """停止监听"""
        if not self._is_running:
            return
        
        if self.listener:
            self.listener.stop()
            self._is_running = False
            logger.info("热键监听已停止")
    
    def _on_press(self, key):
        """按键按下事件"""
        try:
            import time
            
            key_name = self._get_key_name(key)
            if not key_name:
                return
                
            self._current_keys.add(key_name)
            
            # 调试：显示当前按键组合
            logger.debug(f"当前按键: {sorted(self._current_keys)}")
            
            # 检查是否匹配已注册的热键
            current = frozenset(self._current_keys)
            if current in self.callbacks:
                # 防抖检查：如果最近刚触发过，就忽略
                current_time = time.time()
                last_time = self._last_trigger_time.get(current, 0)
                
                if current_time - last_time >= self._debounce_interval:
                    # 更新触发时间
                    self._last_trigger_time[current] = current_time
                    logger.info(f"热键匹配: {sorted(self._current_keys)}")
                    callback = self.callbacks[current]
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"热键回调执行失败: {e}", exc_info=True)
                    finally:
                        # 触发后立即清空按键集合，防止残留
                        logger.info(f"触发后清空按键集合，清空前: {sorted(self._current_keys)}")
                        self._current_keys.clear()
                        logger.info("按键集合已清空")
                else:
                    logger.info(f"热键触发过快，忽略: {sorted(self._current_keys)}")
        
        except Exception as e:
            logger.error(f"热键处理错误: {e}", exc_info=True)
    
    def _on_release(self, key):
        """按键释放事件"""
        try:
            key_name = self._get_key_name(key)
            if not key_name:
                return
                
            logger.debug(f"按键释放: {key_name}, 释放前: {sorted(self._current_keys)}")
            self._current_keys.discard(key_name)
            logger.debug(f"释放后: {sorted(self._current_keys)}")
            
        except Exception as e:
            logger.error(f"按键释放处理错误: {e}")
    
    def _get_key_name(self, key) -> str:
        """获取按键名称"""
        try:
            if isinstance(key, keyboard.KeyCode):
                # 字符键
                if key.char:
                    return key.char.lower()
                # 如果没有char属性，尝试使用vk（虚拟键码）
                elif hasattr(key, 'vk') and key.vk:
                    # 数字键0-9的vk码
                    if 48 <= key.vk <= 57:  # 0-9
                        return chr(key.vk)
                    # 小键盘数字
                    elif 96 <= key.vk <= 105:  # 小键盘0-9
                        return chr(key.vk - 48)
                return None
            else:
                # 特殊键
                if not hasattr(key, 'name'):
                    return None
                    
                name = key.name.lower()
                # 统一左右修饰键
                if name in ['ctrl_l', 'ctrl_r']:
                    return 'ctrl'
                elif name in ['shift_l', 'shift_r']:
                    return 'shift'
                elif name in ['alt_l', 'alt_r']:
                    return 'alt'
                return name
        except Exception as e:
            logger.debug(f"按键识别错误: {e}")
            return None
    
    def _parse_hotkey(self, hotkey: str) -> list:
        """
        解析热键字符串
        
        Args:
            hotkey: 如 "ctrl+shift+q"
            
        Returns:
            按键列表，如 ['ctrl', 'shift', 'q']
        """
        parts = hotkey.lower().split('+')
        keys = []
        for part in parts:
            part = part.strip()
            if part in ['ctrl', 'shift', 'alt', 'cmd', 'win']:
                keys.append(part)
            else:
                keys.append(part)
        return keys

