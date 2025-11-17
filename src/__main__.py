"""
应用程序入口点
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from loguru import logger

from src.utils.config_loader import config
from src.utils.logger import setup_logger
from src.ui.tray_icon import TrayIcon
from src.core.hotkey_manager import HotkeyManager
from src.core.clipboard_monitor import ClipboardMonitor
from src.ui.popup_window import PopupWindow
from src.ui.main_window import MainWindow
from src.ui.screenshot_window import ScreenshotWindow
from src.core.ocr_extractor import OCRExtractor


class TranslateSignals(QObject):
    """用于跨线程触发翻译的信号"""
    translate_requested = pyqtSignal(str)


class Application:
    """主应用程序类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(config.app.name)
        self.app.setApplicationVersion(config.app.version)

        # 初始化组件
        self.popup_window = PopupWindow()
        self.main_window = MainWindow()
        self.hotkey_manager = HotkeyManager()
        self.clipboard_monitor = ClipboardMonitor()
        self.tray_icon = TrayIcon()
        self.screenshot_window = ScreenshotWindow()
        self.ocr_extractor = OCRExtractor()

        # 学习时长追踪
        from src.utils.activity_tracker import get_activity_tracker
        self.activity_tracker = get_activity_tracker()

        # 创建信号对象（用于跨线程通信）
        self.signals = TranslateSignals()
        self.signals.translate_requested.connect(self._do_translate)

        self._setup_connections()
        self._register_hotkeys()
        
    def _setup_connections(self):
        """设置组件间连接"""
        # 托盘图标点击事件
        self.tray_icon.show_main_window.connect(self.main_window.show)
        self.tray_icon.quit_app.connect(self.quit)
        
        # 剪贴板监听事件
        self.clipboard_monitor.text_copied.connect(self._on_text_copied)
        
    def _register_hotkeys(self):
        """注册全局热键"""
        # 翻译热键
        self.hotkey_manager.register(
            config.hotkey.translate,
            self._on_translate_hotkey
        )
        
        # 打开主窗口热键
        self.hotkey_manager.register(
            config.hotkey.open_main_window,
            self._on_open_main_window
        )
        
        # 切换剪贴板监听热键
        self.hotkey_manager.register(
            config.hotkey.toggle_monitor,
            self._on_toggle_monitor
        )
        
        # OCR截图热键
        self.hotkey_manager.register(
            config.hotkey.screenshot_ocr,
            self._on_screenshot_ocr
        )
        
    def _on_translate_hotkey(self):
        """翻译热键回调（在pynput线程中调用）"""
        logger.info("=========== 翻译热键被触发 ===========")
        from src.core.text_extractor import TextExtractor
        from src.services.context_service import ContextService

        try:
            # 黑名单检查
            context_info = ContextService.get_active_window_info()
            if context_info:
                app_name = context_info.get('app_name', '')
                if ContextService.is_blacklisted(app_name):
                    logger.info(f"应用 '{app_name}' 在黑名单中，取消翻译")
                    return

            text = TextExtractor.extract_selected_text()
            logger.info(f"提取到的文本: '{text}'")

            if text:
                logger.info(f"发送翻译请求信号: {text[:50]}...")
                # 通过信号发送到主线程
                self.signals.translate_requested.emit(text)
            else:
                logger.warning("未提取到文本，可能没有选中文字")
        except Exception as e:
            logger.error(f"翻译热键处理失败: {e}", exc_info=True)
    
    def _do_translate(self, text: str):
        """实际执行翻译（在主线程中调用）"""
        logger.info(f"主线程收到翻译请求: {text[:50]}...")
        try:
            # 记录学习活动
            self.activity_tracker.record_activity()

            self.popup_window.show_translation(text)
            logger.info("翻译窗口已调用")
        except Exception as e:
            logger.error(f"翻译执行失败: {e}", exc_info=True)
            
    def _on_open_main_window(self):
        """打开主窗口"""
        self.main_window.show()
        self.main_window.activateWindow()
        
    def _on_toggle_monitor(self):
        """切换剪贴板监听"""
        if self.clipboard_monitor.is_monitoring:
            self.clipboard_monitor.stop()
            logger.info("剪贴板监听已停止")
        else:
            self.clipboard_monitor.start()
            logger.info("剪贴板监听已启动")
            
    def _on_text_copied(self, text: str):
        """剪贴板文本变化回调"""
        if text:
            logger.info(f"剪贴板监听到文本: {text[:50]}...")
            self.popup_window.show_translation(text)
    
    def _on_screenshot_ocr(self):
        """OCR截图热键回调"""
        if not self.ocr_extractor.is_available():
            logger.warning("OCR功能不可用，请安装: pip install paddleocr")
            return
        
        logger.info("启动OCR截图")
        
        # 连接信号
        self.screenshot_window.region_selected.connect(self._on_region_selected)
        
        # 开始截图
        self.screenshot_window.start_capture()
    
    def _on_region_selected(self, region):
        """选区确定回调"""
        try:
            import tempfile
            from pathlib import Path
            from PyQt6.QtWidgets import QApplication
            
            # 截取选区
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0)
            cropped = screenshot.copy(region)
            
            # 保存临时文件
            temp_dir = Path(tempfile.gettempdir())
            temp_file = temp_dir / "translearn_ocr_temp.png"
            cropped.save(str(temp_file))
            
            logger.debug(f"截图已保存: {temp_file}")
            
            # OCR识别
            text = self.ocr_extractor.extract_text_from_image(str(temp_file))
            
            # 删除临时文件
            try:
                temp_file.unlink()
            except:
                pass
            
            # 显示翻译
            if text:
                logger.info(f"OCR识别文本: {text[:50]}...")
                self.popup_window.show_translation(text)
            else:
                logger.warning("OCR未识别到文字")
        
        except Exception as e:
            logger.error(f"OCR处理失败: {e}")
            
    def run(self):
        """运行应用程序"""
        logger.info("应用程序启动")

        # 启动学习会话
        self.activity_tracker.start_session()

        # 启动热键监听
        self.hotkey_manager.start()

        # 启动剪贴板监听(如果配置启用)
        if config.features.clipboard_monitor:
            self.clipboard_monitor.start()

        # 显示托盘图标
        self.tray_icon.show()

        # 进入事件循环
        return self.app.exec()
        
    def quit(self):
        """退出应用程序"""
        logger.info("应用程序退出")

        # 结束学习会话并保存时长
        self.activity_tracker.end_session()

        self.hotkey_manager.stop()
        self.clipboard_monitor.stop()
        self.app.quit()


def main():
    """主函数"""
    try:
        # 设置日志
        setup_logger()
        
        # 创建并运行应用
        app = Application()
        sys.exit(app.run())
        
    except Exception as e:
        logger.exception(f"应用程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

