# API 文档

## 核心服务 API

### TranslationService - 翻译服务

翻译服务的门面类，提供统一的翻译接口。

#### translate()

```python
async def translate(
    text: str,
    source_lang: Optional[str] = None,
    target_lang: str = "zh",
    save_to_db: bool = False,
    context: Optional[dict] = None
) -> TranslationResult
```

**参数:**
- `text`: 待翻译文本
- `source_lang`: 源语言（None 则自动检测）
- `target_lang`: 目标语言
- `save_to_db`: 是否保存到数据库
- `context`: 上下文信息（来源、URL 等）

**返回:**
- `TranslationResult`: 翻译结果对象

**示例:**

```python
from src.services.translation_service import TranslationService

service = TranslationService()
result = await service.translate("Hello world")
print(result.translation)  # 你好世界
```

## 数据访问 API

### EntryRepository - 词条仓储

管理词条数据的增删改查。

#### save()

```python
def save(entry: Entry) -> Entry
```

保存或更新词条。如果词条已存在则更新，否则新增。

#### get_by_id()

```python
def get_by_id(entry_id: int) -> Optional[Entry]
```

根据 ID 获取词条。

#### get_all()

```python
def get_all(limit: int = 100, offset: int = 0) -> List[Entry]
```

获取所有词条（分页）。

#### search()

```python
def search(keyword: str, limit: int = 50) -> List[Entry]
```

搜索词条（在原文和翻译中搜索）。

#### get_review_list()

```python
def get_review_list(limit: int = 50) -> List[Entry]
```

获取待复习列表。

**示例:**

```python
from src.data.repository import EntryRepository
from src.data.models import Entry

repo = EntryRepository()

# 保存词条
entry = Entry(
    source_text="hello",
    translation="你好",
    source_lang="en",
    target_lang="zh"
)
repo.save(entry)

# 搜索
results = repo.search("hello")
```

### CacheRepository - 缓存仓储

管理翻译缓存。

#### get()

```python
def get(cache_key: str) -> Optional[TranslationCache]
```

获取缓存，自动检查过期并增加命中次数。

#### set()

```python
def set(cache: TranslationCache)
```

设置缓存。

#### clean_expired()

```python
def clean_expired()
```

清理过期缓存。

### StatsRepository - 统计仓储

管理统计数据。

#### update_today_stats()

```python
def update_today_stats(**kwargs)
```

更新今日统计数据。

**示例:**

```python
stats_repo.update_today_stats(
    new_words=1,
    translation_count=1,
    ai_calls=1
)
```

#### get_stats()

```python
def get_stats(days: int = 30) -> List[DailyStat]
```

获取最近 N 天的统计数据。

## 核心业务 API

### HotkeyManager - 热键管理器

管理全局热键。

#### register()

```python
def register(hotkey: str, callback: Callable)
```

注册热键。

**参数:**
- `hotkey`: 热键字符串，如 "ctrl+q"
- `callback`: 回调函数

**示例:**

```python
from src.core.hotkey_manager import HotkeyManager

manager = HotkeyManager()

def on_translate():
    print("翻译热键触发")

manager.register("ctrl+q", on_translate)
manager.start()
```

#### start() / stop()

启动/停止热键监听。

### TextExtractor - 文本提取器

提取选中的文本。

#### extract_selected_text()

```python
@staticmethod
def extract_selected_text() -> str
```

提取当前选中的文本（不污染剪贴板）。

**返回:**
- `str`: 提取的文本

**示例:**

```python
from src.core.text_extractor import TextExtractor

text = TextExtractor.extract_selected_text()
print(f"提取到: {text}")
```

### ClipboardMonitor - 剪贴板监听器

监听剪贴板变化。

#### 信号

- `text_copied`: 当检测到文本变化时发射

**示例:**

```python
from src.core.clipboard_monitor import ClipboardMonitor

monitor = ClipboardMonitor()

def on_text_copied(text: str):
    print(f"检测到文本: {text}")

monitor.text_copied.connect(on_text_copied)
monitor.start()
```

### SmartRouter - 智能路由器

选择合适的翻译器。

#### choose_translator()

```python
def choose_translator(text: str, source_lang: str) -> TranslatorType
```

根据文本类型智能选择翻译器。

**返回:**
- `TranslatorType`: LOCAL_DICT / ONLINE_DICT / AI

#### detect_language()

```python
async def detect_language(text: str) -> str
```

检测文本语言。

## 数据模型

### TranslationResult

翻译结果数据类。

```python
@dataclass
class TranslationResult:
    translation: str                      # 翻译结果
    source_lang: str = "en"               # 源语言
    target_lang: str = "zh"               # 目标语言
    entry_type: str = "sentence"          # 类型
    explanation: Optional[str] = None     # 补充说明
    pronunciation: Optional[str] = None   # 发音
    examples: Optional[list] = None       # 例句
    domain: Optional[str] = None          # 领域
    translator_type: Optional[str] = None # 翻译器类型
    translation_time: Optional[float] = None # 翻译耗时
```

### Entry

词条模型（SQLAlchemy ORM）。

主要字段见 [DATABASE.md](DATABASE.md)。

## 配置 API

### Config

全局配置对象。

```python
from src.utils.config_loader import config

# 访问配置
print(config.app.name)
print(config.database.host)
print(config.hotkey.translate)
print(config.translation.ai.model)
```

配置结构见 `src/utils/config_loader.py`。

## 扩展开发

### 自定义翻译器

实现 `TranslatorInterface` 接口:

```python
from src.core.translator_interface import TranslatorInterface, TranslationResult

class MyTranslator(TranslatorInterface):
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        # 实现翻译逻辑
        translation = "..."
        
        return TranslationResult(
            translation=translation,
            source_lang=source_lang,
            target_lang=target_lang
        )
    
    def get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        import hashlib
        key_str = f"my:{text}:{source_lang}:{target_lang}"
        return hashlib.md5(key_str.encode()).hexdigest()
```

### 数据库扩展

添加新表:

```python
from src.data.database import Base
from sqlalchemy import Column, Integer, String

class MyTable(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

创建表:

```python
from src.data.database import db_manager

db_manager.create_all_tables()
```

