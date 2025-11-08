"""
配置加载器
"""
from pathlib import Path
from typing import Optional
import toml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AppConfig(BaseModel):
    """应用配置"""
    name: str = "TransLearn"
    version: str = "1.0.0"
    language: str = "zh_CN"
    theme: str = "auto"


class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "translearn"
    charset: str = "utf8mb4"
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600


class HotkeyConfig(BaseModel):
    """热键配置"""
    translate: str = "ctrl+q"
    screenshot_ocr: str = "ctrl+shift+q"
    toggle_monitor: str = "ctrl+shift+t"
    open_main_window: str = "ctrl+shift+l"


class AIConfig(BaseModel):
    """AI翻译配置"""
    provider: str = "dashscope"
    model: str = "qwen-turbo"
    api_key: str = ""
    base_url: str = ""
    timeout: int = 15
    max_tokens: int = 500
    temperature: float = 0.3


class OnlineDictConfig(BaseModel):
    """在线词典配置"""
    provider: str = "youdao"
    api_key: str = ""
    timeout: int = 5


class LocalDictConfig(BaseModel):
    """本地词典配置"""
    enabled: bool = True


class TranslationConfig(BaseModel):
    """翻译配置"""
    priority: list[str] = ["local_dict", "online_dict", "ai"]
    force_ai: bool = False
    auto_detect_language: bool = True
    word_threshold: int = 1
    phrase_threshold: int = 5
    sentence_min_length: int = 10
    ai: AIConfig = Field(default_factory=AIConfig)
    online_dict: OnlineDictConfig = Field(default_factory=OnlineDictConfig)
    local_dict: LocalDictConfig = Field(default_factory=LocalDictConfig)


class PopupConfig(BaseModel):
    """悬浮窗配置"""
    position: str = "mouse"
    offset_x: int = 10
    offset_y: int = 10
    width: int = 450
    max_height: int = 600
    opacity: float = 0.95
    auto_hide: bool = False
    auto_hide_delay: int = 0
    show_animation: bool = True
    theme: str = "auto"


class MainWindowConfig(BaseModel):
    """主窗口配置"""
    width: int = 1000
    height: int = 700
    default_view: str = "timeline"


class UIConfig(BaseModel):
    """UI配置"""
    popup: PopupConfig = Field(default_factory=PopupConfig)
    main_window: MainWindowConfig = Field(default_factory=MainWindowConfig)


class FeaturesConfig(BaseModel):
    """功能配置"""
    clipboard_monitor: bool = True
    clipboard_delay: int = 300
    clipboard_filter_duplicates: bool = True
    clipboard_filter_paths: bool = True
    auto_save: bool = True
    auto_save_threshold: int = 3
    play_sound: bool = False
    pronunciation: bool = True
    context_capture: bool = True


class ReviewConfig(BaseModel):
    """复习配置"""
    algorithm: str = "sm2"
    daily_goal: int = 50
    notification_enabled: bool = True
    notification_time: str = "20:00"


class CacheConfig(BaseModel):
    """缓存配置"""
    enabled: bool = True
    expire_days: int = 30
    max_size_mb: int = 100


class BlacklistConfig(BaseModel):
    """黑名单配置"""
    apps: list[str] = ["PasswordManager", "Bitwarden", "KeePass"]
    auto_add: bool = True


class DataConfig(BaseModel):
    """数据配置"""
    backup_enabled: bool = True
    backup_interval_days: int = 7
    export_format: str = "csv"


class PerformanceConfig(BaseModel):
    """性能配置"""
    max_concurrent_translations: int = 3
    log_level: str = "INFO"


class Config(BaseSettings):
    """主配置类"""
    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    hotkey: HotkeyConfig = Field(default_factory=HotkeyConfig)
    translation: TranslationConfig = Field(default_factory=TranslationConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    blacklist: BlacklistConfig = Field(default_factory=BlacklistConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """从文件加载配置"""
        if config_path is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "data" / "config.toml"
            
        if not config_path.exists():
            # 如果配置文件不存在，使用示例配置
            example_path = config_path.parent / "config.example.toml"
            if example_path.exists():
                print(f"警告: 配置文件 {config_path} 不存在，使用默认配置")
                return cls()
            else:
                print(f"警告: 配置文件和示例配置都不存在，使用默认配置")
                return cls()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = toml.load(f)
            return cls(**config_dict)
        except Exception as e:
            print(f"警告: 加载配置文件失败 ({e})，使用默认配置")
            return cls()


# 全局配置实例
config = Config.load_from_file()

