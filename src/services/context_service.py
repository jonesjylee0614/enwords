"""
上下文捕获服务
获取活动窗口信息、应用名称、URL等
"""
import platform
from typing import Optional, Dict, List
from loguru import logger
from src.utils.config_loader import config


class ContextService:
    """上下文捕获服务"""
    
    @staticmethod
    def get_active_window_info() -> Optional[Dict[str, str]]:
        """
        获取活动窗口信息
        
        Returns:
            包含窗口信息的字典，或 None
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                return ContextService._get_windows_info()
            elif system == "Darwin":
                return ContextService._get_macos_info()
            elif system == "Linux":
                return ContextService._get_linux_info()
            else:
                logger.warning(f"不支持的系统: {system}")
                return None
        
        except Exception as e:
            logger.error(f"获取活动窗口信息失败: {e}")
            return None
    
    @staticmethod
    def _get_windows_info() -> Optional[Dict[str, str]]:
        """获取 Windows 活动窗口信息"""
        try:
            import win32gui
            import win32process
            import psutil
            
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            
            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)
            
            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # 获取进程名称
            process = psutil.Process(pid)
            app_name = process.name()
            
            # 提取URL（如果是浏览器）
            url = None
            if "chrome" in app_name.lower() or "firefox" in app_name.lower() or "edge" in app_name.lower():
                # 简单从标题提取URL（不完美）
                if " - " in window_title:
                    url = window_title.split(" - ")[0]
            
            return {
                "app_name": app_name,
                "window_title": window_title,
                "url": url
            }
        
        except Exception as e:
            logger.error(f"获取 Windows 窗口信息失败: {e}")
            return None
    
    @staticmethod
    def _get_macos_info() -> Optional[Dict[str, str]]:
        """获取 macOS 活动窗口信息"""
        try:
            from AppKit import NSWorkspace
            
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            
            app_name = active_app['NSApplicationName']
            
            return {
                "app_name": app_name,
                "window_title": "",
                "url": None
            }
        
        except Exception as e:
            logger.error(f"获取 macOS 窗口信息失败: {e}")
            return None
    
    @staticmethod
    def _get_linux_info() -> Optional[Dict[str, str]]:
        """获取 Linux 活动窗口信息"""
        try:
            import subprocess
            
            # 使用 xdotool 获取活动窗口
            window_id = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            
            # 获取窗口标题
            window_title = subprocess.check_output(
                ["xdotool", "getwindowname", window_id]
            ).decode().strip()
            
            # 获取PID
            pid = subprocess.check_output(
                ["xdotool", "getwindowpid", window_id]
            ).decode().strip()
            
            # 获取进程名
            import psutil
            process = psutil.Process(int(pid))
            app_name = process.name()
            
            return {
                "app_name": app_name,
                "window_title": window_title,
                "url": None
            }
        
        except Exception as e:
            logger.error(f"获取 Linux 窗口信息失败: {e}")
            return None
    
    @staticmethod
    def get_blacklist() -> List[str]:
        """
        获取完整的黑名单列表（配置文件 + 数据库）

        Returns:
            黑名单应用列表
        """
        blacklist = []

        # 1. 从配置文件获取
        try:
            if hasattr(config, 'blacklist') and hasattr(config.blacklist, 'apps'):
                blacklist.extend(config.blacklist.apps)
        except Exception as e:
            logger.debug(f"读取配置黑名单失败: {e}")

        # 2. 从数据库获取
        try:
            from src.data.database import db_manager
            from src.data.models import Blacklist

            with db_manager.get_session() as session:
                db_blacklist = session.query(Blacklist).all()
                blacklist.extend([item.app_name for item in db_blacklist])
        except Exception as e:
            logger.debug(f"读取数据库黑名单失败: {e}")

        return list(set(blacklist))  # 去重

    @staticmethod
    def is_blacklisted(app_name: str, blacklist: Optional[List[str]] = None) -> bool:
        """
        检查应用是否在黑名单中

        Args:
            app_name: 应用名称
            blacklist: 黑名单列表（可选，不提供则自动获取）

        Returns:
            是否在黑名单中
        """
        if not app_name:
            return False

        # 如果没有提供黑名单，自动获取
        if blacklist is None:
            blacklist = ContextService.get_blacklist()

        if not blacklist:
            return False

        app_name_lower = app_name.lower()

        for blacklisted in blacklist:
            if blacklisted.lower() in app_name_lower:
                logger.info(f"应用 '{app_name}' 在黑名单中，跳过翻译")
                return True

        return False

    @staticmethod
    def should_capture(app_name: str) -> bool:
        """
        判断是否应该捕获该应用的内容

        Args:
            app_name: 应用名称

        Returns:
            是否应该捕获
        """
        return not ContextService.is_blacklisted(app_name)

