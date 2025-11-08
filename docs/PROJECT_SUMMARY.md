# 项目总结文档

## 项目信息

**项目名称**: TransLearn - Windows 个人翻译学习工具  
**版本**: v1.0.0  
**开发时间**: 2025年  
**技术栈**: Python 3.10 + PyQt6 + MySQL 5.7 + SQLAlchemy

## 项目概述

TransLearn 是一个专为 Windows 平台设计的翻译学习工具，集成了即时翻译、智能词库和科学复习功能。

### 核心特性

1. **即时翻译**
   - 全局热键取词（Ctrl+Q）
   - 剪贴板智能监听
   - OCR 截图翻译（规划中）

2. **智能引擎**
   - 本地词典 + 在线词典 + AI 混合翻译
   - 智能路由自动选择最佳翻译器
   - 翻译结果缓存优化

3. **个人词库**
   - 自动积累翻译历史
   - 标签分类管理
   - 全文搜索

4. **数据管理**
   - MySQL 本地存储
   - 数据统计分析
   - 备份恢复

## 项目结构

```
TransLearn/
├─ src/                     # 源代码
│  ├─ ui/                   # UI层
│  │  ├─ popup_window.py    # 翻译悬浮窗
│  │  ├─ main_window.py     # 主窗口
│  │  └─ tray_icon.py       # 托盘图标
│  ├─ services/             # 服务层
│  │  └─ translation_service.py
│  ├─ core/                 # 核心业务
│  │  ├─ hotkey_manager.py
│  │  ├─ clipboard_monitor.py
│  │  ├─ text_extractor.py
│  │  ├─ ai_translator.py
│  │  ├─ smart_router.py
│  │  └─ language_detector.py
│  ├─ data/                 # 数据层
│  │  ├─ database.py
│  │  ├─ models.py
│  │  └─ repository.py
│  └─ utils/                # 工具
│     ├─ config_loader.py
│     └─ logger.py
├─ data/                    # 数据目录
│  ├─ config.example.toml
│  └─ logs/
├─ scripts/                 # 脚本
│  ├─ init_database.py
│  ├─ setup_dev.py
│  └─ create_database.sql
├─ docs/                    # 文档
│  ├─ DATABASE.md
│  ├─ USAGE.md
│  ├─ API.md
│  └─ ARCHITECTURE.md
├─ requirements.txt         # 依赖
├─ requirements-dev.txt
├─ pyproject.toml
├─ README.md
└─ run.bat                  # 启动脚本
```

## 技术实现

### 1. 数据库设计（MySQL）

**核心表:**
- `entries`: 词条表（翻译历史）
- `tags`: 标签表
- `daily_stats`: 每日统计
- `translation_cache`: 翻译缓存
- `settings`: 配置表
- `blacklist`: 黑名单

**特点:**
- 使用 utf8mb4 支持 emoji
- 索引优化查询性能
- 软删除保留历史
- 全文搜索支持（规划中）

### 2. 配置管理

使用 Pydantic + TOML:
- 类型安全
- 自动验证
- 易于扩展

配置文件: `data/config.toml`

### 3. 翻译引擎

**智能路由逻辑:**
```
单词(≤1个词) → 本地词典
短语(2-5个词) → 在线词典  
句子/段落 → AI翻译
```

**支持的 AI 提供商:**
- OpenAI (GPT系列)
- DashScope (通义千问)
- 可扩展到 Ollama 等

### 4. 热键系统

使用 pynput 实现全局热键:
- `Ctrl+Q`: 翻译选中文本
- `Ctrl+Shift+Q`: OCR 截图翻译
- `Ctrl+Shift+T`: 切换剪贴板监听
- `Ctrl+Shift+L`: 打开主窗口

### 5. 剪贴板监听

智能过滤:
- 过滤文件路径
- 过滤重复内容
- 过滤超长文本
- 延迟触发避免误触

### 6. UI 设计

基于 PyQt6:
- 现代化设计
- 流畅动画
- 响应式布局
- 符合 Windows 11 风格

## 已实现功能

### ✅ 核心功能
- [x] 全局热键取词
- [x] 文本提取（不污染剪贴板）
- [x] 剪贴板监听
- [x] AI 翻译（OpenAI/DashScope）
- [x] 语言自动检测
- [x] 智能翻译路由
- [x] 翻译结果缓存

### ✅ 数据管理
- [x] MySQL 数据库集成
- [x] SQLAlchemy ORM
- [x] 词条保存与查询
- [x] 仓储模式封装
- [x] 数据库初始化脚本

### ✅ 用户界面
- [x] 翻译悬浮窗
- [x] 主窗口（词库浏览）
- [x] 系统托盘图标
- [x] 美观的UI设计

### ✅ 配置与工具
- [x] 完整的配置系统
- [x] 日志管理（loguru）
- [x] 开发环境设置脚本
- [x] 项目文档

## 待实现功能

### ⏳ Phase 1
- [ ] 在线词典集成（有道/金山）
- [ ] 本地词典（离线查询）
- [ ] OCR 截图识别
- [ ] 发音功能（TTS）

### ⏳ Phase 2
- [ ] SM-2 复习算法
- [ ] 复习界面
- [ ] 学习统计图表
- [ ] 数据导出（CSV/JSON/Anki）

### ⏳ Phase 3
- [ ] 设置界面
- [ ] 主题切换（明亮/暗色）
- [ ] 多语言支持
- [ ] 插件系统
- [ ] 云同步（可选）

## 快速开始

### 1. 环境准备

```bash
# Python 3.10+
# MySQL 5.7+
```

### 2. 安装

```bash
# 克隆项目
git clone <repository_url>
cd translearn

# 安装依赖
pip install -r requirements.txt

# 创建数据库
mysql -u root -p < scripts/create_database.sql

# 配置
cp data/config.example.toml data/config.toml
# 编辑 data/config.toml，配置数据库和 API Key

# 初始化数据库
python scripts/init_database.py

# 运行
python -m src
```

### 3. 使用

1. 启动应用后会在系统托盘显示图标
2. 选中任意文本，按 `Ctrl+Q` 翻译
3. 双击托盘图标打开主窗口
4. 在主窗口查看词库和统计

## 配置说明

### 数据库配置

```toml
[database]
host = "localhost"
port = 3306
user = "root"
password = "your_password"
database = "translearn"
```

### AI 配置

```toml
[translation.ai]
provider = "dashscope"  # 或 "openai"
model = "qwen-turbo"
api_key = "your_api_key"
```

### 热键配置

```toml
[hotkey]
translate = "ctrl+q"
screenshot_ocr = "ctrl+shift+q"
toggle_monitor = "ctrl+shift+t"
open_main_window = "ctrl+shift+l"
```

## 开发说明

### 开发环境

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/

# 运行测试
pytest
```

### 项目规范

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串
- 提交前运行测试

### 添加新功能

1. 在对应层创建模块
2. 实现业务逻辑
3. 编写单元测试
4. 更新文档

## 常见问题

### 1. 数据库连接失败

- 确认 MySQL 已启动
- 检查配置文件
- 确认数据库已创建

### 2. 热键不生效

- 检查快捷键冲突
- 以管理员身份运行
- 修改配置中的快捷键

### 3. 翻译失败

- 检查网络连接
- 确认 API Key 正确
- 查看日志文件

## 性能指标

### 目标
- 热键响应: < 100ms
- 词典翻译: < 200ms
- AI 翻译: < 2s
- 内存占用: < 150MB
- CPU 占用: < 5% (闲置)

### 优化措施
- 翻译结果缓存
- 数据库连接池
- 异步并发处理
- 智能路由避免 AI 调用

## 安全性

### 数据安全
- 本地存储，不上传云端
- 可选加密敏感数据
- 软删除保留历史

### 隐私保护
- 黑名单机制（密码管理器等）
- 可配置监听范围
- 不记录敏感应用

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目主页: [GitHub](https://github.com/yourusername/translearn)
- 问题反馈: [Issues](https://github.com/yourusername/translearn/issues)

## 致谢

感谢以下开源项目:
- PyQt6
- SQLAlchemy
- pynput
- loguru
- OpenAI / DashScope

---

**项目状态**: ✅ MVP 完成，持续开发中

**最后更新**: 2025年11月

