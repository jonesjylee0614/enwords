# 架构设计文档

## 概述

TransLearn 采用经典的分层架构设计，确保代码清晰、可维护、可扩展。

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层 (UI Layer)                      │
│  src/ui/                                                     │
│  - popup_window.py    翻译悬浮窗                              │
│  - main_window.py     主窗口                                  │
│  - tray_icon.py       系统托盘                                │
├─────────────────────────────────────────────────────────────┤
│                   应用服务层 (Service Layer)                  │
│  src/services/                                               │
│  - translation_service.py  翻译服务门面                       │
├─────────────────────────────────────────────────────────────┤
│                   核心业务层 (Core Layer)                     │
│  src/core/                                                   │
│  - hotkey_manager.py       热键管理                           │
│  - clipboard_monitor.py    剪贴板监听                         │
│  - text_extractor.py       文本提取                           │
│  - ai_translator.py        AI翻译器                           │
│  - smart_router.py         智能路由                           │
│  - language_detector.py    语言检测                           │
├─────────────────────────────────────────────────────────────┤
│                   数据访问层 (Data Layer)                     │
│  src/data/                                                   │
│  - database.py        数据库管理                              │
│  - models.py          数据模型(ORM)                           │
│  - repository.py      仓储模式                                │
├─────────────────────────────────────────────────────────────┤
│                   工具层 (Utils Layer)                        │
│  src/utils/                                                  │
│  - config_loader.py   配置加载                                │
│  - logger.py          日志工具                                │
├─────────────────────────────────────────────────────────────┤
│                   基础设施层 (Infrastructure)                 │
│  - MySQL 5.7          数据存储                                │
│  - PyQt6              GUI框架                                │
│  - OpenAI/DashScope   AI服务                                 │
└─────────────────────────────────────────────────────────────┘
```

## 设计模式

### 1. 分层架构（Layered Architecture）

**优势:**
- 关注点分离
- 易于测试
- 便于维护

**层次职责:**

#### UI层
- 用户交互
- 界面展示
- 事件处理

#### Service层
- 业务编排
- 事务管理
- 门面模式

#### Core层
- 核心业务逻辑
- 算法实现
- 外部API集成

#### Data层
- 数据持久化
- 缓存管理
- 查询封装

### 2. 仓储模式（Repository Pattern）

将数据访问逻辑封装在仓储类中。

```python
class EntryRepository:
    def save(self, entry: Entry) -> Entry:
        """保存词条"""
        pass
    
    def get_by_id(self, entry_id: int) -> Optional[Entry]:
        """根据ID获取"""
        pass
```

**优势:**
- 统一数据访问接口
- 便于切换数据源
- 易于单元测试

### 3. 门面模式（Facade Pattern）

`TranslationService` 作为翻译功能的门面。

```python
class TranslationService:
    def __init__(self):
        self.ai_translator = AITranslator()
        self.router = SmartRouter()
        self.cache_repo = CacheRepository()
        # ...
    
    async def translate(self, text: str) -> TranslationResult:
        """统一的翻译接口"""
        pass
```

**优势:**
- 简化客户端调用
- 隐藏内部复杂性
- 统一错误处理

### 4. 策略模式（Strategy Pattern）

不同的翻译器实现统一接口。

```python
class TranslatorInterface(ABC):
    @abstractmethod
    async def translate(self, text: str, ...) -> TranslationResult:
        pass

class AITranslator(TranslatorInterface):
    """AI翻译实现"""
    pass

class DictTranslator(TranslatorInterface):
    """词典翻译实现"""
    pass
```

**优势:**
- 算法可替换
- 易于扩展
- 符合开闭原则

### 5. 单例模式（Singleton Pattern）

数据库管理器使用单例。

```python
class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**优势:**
- 全局唯一实例
- 统一资源管理
- 避免重复连接

### 6. 观察者模式（Observer Pattern）

使用 PyQt6 信号槽机制。

```python
class ClipboardMonitor(QObject):
    # 信号定义
    text_copied = pyqtSignal(str)
    
    def _monitor_loop(self):
        # 检测到变化时发射信号
        self.text_copied.emit(text)

# 使用
monitor = ClipboardMonitor()
monitor.text_copied.connect(on_text_copied)
```

**优势:**
- 松耦合
- 事件驱动
- 易于扩展

## 核心流程

### 翻译流程

```
1. 用户触发（热键/剪贴板）
   ↓
2. 文本提取
   ↓
3. TranslationService.translate()
   ↓
4. 检查缓存
   ↓
5. 语言检测
   ↓
6. 智能路由选择翻译器
   ↓
7. 执行翻译
   ↓
8. 缓存结果
   ↓
9. 保存到数据库（可选）
   ↓
10. 更新统计
   ↓
11. 显示结果
```

### 数据流

```
┌─────────┐
│  用户   │
└────┬────┘
     │ 操作
     ↓
┌─────────┐
│   UI    │ ←─── 显示结果
└────┬────┘
     │ 调用
     ↓
┌─────────┐
│ Service │ ←─── 业务编排
└────┬────┘
     │ 使用
     ↓
┌─────────┐
│  Core   │ ←─── 核心逻辑
└────┬────┘
     │ 访问
     ↓
┌─────────┐
│  Data   │ ←─── 数据持久化
└────┬────┘
     │
     ↓
┌─────────┐
│  MySQL  │
└─────────┘
```

## 技术栈

### 前端（UI）
- **PyQt6**: 现代化 GUI 框架
- **QSS**: Qt样式表，类似 CSS

### 后端（业务逻辑）
- **Python 3.10+**: 主要开发语言
- **asyncio**: 异步编程
- **pynput**: 全局热键
- **pyperclip**: 剪贴板操作

### 数据存储
- **MySQL 5.7+**: 主数据库
- **SQLAlchemy**: ORM 框架
- **pymysql**: MySQL 驱动

### 外部服务
- **OpenAI API**: GPT 翻译
- **DashScope**: 通义千问
- **有道/金山词典**: 在线词典

### 工具库
- **loguru**: 日志管理
- **pydantic**: 配置验证
- **toml**: 配置文件格式

## 扩展点

### 1. 新增翻译器

实现 `TranslatorInterface` 接口:

```python
class CustomTranslator(TranslatorInterface):
    async def translate(self, text, source_lang, target_lang):
        # 实现翻译逻辑
        pass
```

### 2. 新增数据表

继承 `Base` 创建模型:

```python
class CustomTable(Base):
    __tablename__ = "custom_table"
    # 定义字段
```

### 3. 新增UI组件

继承 PyQt6 组件:

```python
class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化UI
```

### 4. 新增服务

在 `src/services/` 下添加:

```python
class CustomService:
    def do_something(self):
        pass
```

## 性能优化

### 1. 数据库
- 连接池复用
- 索引优化
- 批量操作
- 缓存查询结果

### 2. 翻译
- 结果缓存
- 智能路由（避免AI调用）
- 异步并发

### 3. UI
- 虚拟列表（大量数据）
- 懒加载
- 界面缓存

### 4. 内存
- 限制缓存大小
- 定期清理
- 使用生成器

## 安全性

### 1. 数据安全
- 敏感信息加密
- SQL注入防护（ORM）
- 软删除机制

### 2. 隐私保护
- 本地存储
- 黑名单机制
- 可选云同步

### 3. API安全
- API Key 配置文件管理
- 请求超时控制
- 错误重试机制

## 可维护性

### 1. 代码规范
- PEP 8
- 类型注解
- 文档字符串

### 2. 测试
- 单元测试
- 集成测试
- 覆盖率监控

### 3. 日志
- 分级日志
- 文件轮转
- 错误追踪

### 4. 配置管理
- 配置文件分离
- 类型安全（pydantic）
- 环境变量支持

## 部署

### 开发环境
```bash
python -m src
```

### 打包
```bash
pyinstaller --name TransLearn --windowed src/__main__.py
```

### 安装
- 绿色版：解压即用
- 安装版：Inno Setup打包

## 未来规划

### Phase 1 - MVP
- ✅ 基础翻译
- ✅ 热键取词
- ✅ 词库管理

### Phase 2 - 增强
- ⏳ OCR 识别
- ⏳ 发音功能
- ⏳ 复习系统

### Phase 3 - 高级
- ⏳ 云同步
- ⏳ 插件系统
- ⏳ 多语言支持

## 参考资料

- [PyQt6 文档](https://doc.qt.io/qtforpython/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [设计模式](https://refactoring.guru/design-patterns)

