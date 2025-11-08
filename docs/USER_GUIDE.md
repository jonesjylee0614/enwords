# TransLearn 用户使用指南

> 版本: 1.0.0  
> 更新时间: 2025-11-09

## 📖 目录

1. [快速开始](#快速开始)
2. [基本功能](#基本功能)
3. [高级功能](#高级功能)
4. [设置说明](#设置说明)
5. [常见问题](#常见问题)
6. [技巧与窍门](#技巧与窍门)

---

## 快速开始

### 首次安装配置

#### 1. 环境准备

```bash
# 确保已安装 Python 3.10+
python --version

# 确保已安装 MySQL 5.7+
mysql --version
```

#### 2. 安装依赖

```bash
# 进入项目目录
cd D:\WorkSpace\code\2025\enwords

# 创建虚拟环境（可选但推荐）
python -m venv venv
venv\Scripts\activate

# 安装必要依赖
pip install -r requirements.txt
```

#### 3. 数据库配置

**方式一：使用脚本创建（推荐）**
```bash
# 使用root账户登录MySQL
mysql -u root -p

# 执行创建脚本
source scripts/create_database.sql
```

**方式二：手动创建**
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS translearn
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选，也可以使用root）
CREATE USER IF NOT EXISTS 'translearn'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON translearn.* TO 'translearn'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. 配置文件设置

```bash
# 复制配置模板
copy data\config.example.toml data\config.toml

# 使用记事本或其他编辑器打开配置文件
notepad data\config.toml
```

**必须修改的配置项：**

```toml
[database]
host = "localhost"          # MySQL主机地址
port = 3306                 # MySQL端口
user = "translearn"         # 数据库用户名
password = "your_password"  # 数据库密码（修改这里）
database = "translearn"     # 数据库名

[translation.ai]
provider = "openai"         # AI提供商: openai / dashscope / ollama
api_key = "your_api_key"    # AI翻译API密钥（修改这里）
model = "gpt-3.5-turbo"     # 使用的模型
```

#### 5. 初始化数据库

```bash
# 创建数据库表
python scripts/init_database.py

# 导入示例词典（可选）
python scripts/import_dict.py
```

成功后会看到：
```
✅ 数据库初始化完成!
```

#### 6. 启动程序

```bash
# 方式一：使用启动脚本
run.bat

# 方式二：命令行启动
python -m src
```

---

## 基本功能

### 1. 划词翻译

**使用步骤：**
1. 在任意程序中选中要翻译的文本
2. 按下快捷键 `Ctrl+Q`
3. 浮动窗口会在鼠标附近显示翻译结果

**浮动窗口功能：**
- 📖 **发音按钮**：点击播放语音
- ⭐ **收藏按钮**：将词条添加到个人词库
- 📋 **复制按钮**：复制翻译结果
- ❌ **关闭按钮**：关闭浮动窗口（或按 `Esc`）

**特点：**
- ✅ 不污染系统剪贴板
- ✅ 自动识别语言
- ✅ 智能选择翻译器（本地词典/AI翻译）
- ✅ 10秒后自动隐藏

**示例操作：**
```
1. 在浏览器中选中 "Hello World"
2. 按 Ctrl+Q
3. 看到翻译："你好，世界"
4. 点击 ⭐ 收藏到词库
```

---

### 2. 剪贴板监听

**功能说明：**
- 开启后，复制任何文本都会自动触发翻译
- 智能过滤：自动忽略文件路径、图片、超长文本

**启用/关闭：**
```
方法一：按快捷键 Ctrl+Shift+T
方法二：点击系统托盘图标 → 切换监听
```

**配置选项：**
```toml
[features]
enable_clipboard_monitor = true  # 是否默认开启

[clipboard]
filter_paths = true              # 过滤文件路径
filter_images = true             # 过滤图片
max_length = 1000                # 最大文本长度
delay = 500                      # 触发延迟（毫秒）
```

**使用技巧：**
- 📌 在阅读英文文档时开启，遇到不懂的词复制即可翻译
- 📌 在编辑敏感文档时关闭，避免误触
- 📌 使用黑名单功能排除特定应用

---

### 3. 主窗口 - 词库管理

**打开方式：**
```
方法一：按快捷键 Ctrl+Shift+L
方法二：点击系统托盘图标 → 显示主窗口
```

#### 3.1 词库标签页

**查看词条：**
- 显示所有收藏的词条
- 格式：`原文 → 翻译`
- 按创建时间倒序排列

**搜索词条：**
1. 在顶部搜索框输入关键词
2. 实时搜索原文和译文
3. 支持模糊匹配

**查看详情：**
1. 双击任意词条
2. 弹出详情对话框

**词条详情对话框包含：**
- 📝 **原文**：source_text
- 📝 **翻译**：translation  
- 🌍 **语言对**：英文 → 中文
- 📊 **学习数据**：
  - 熟悉度：0-5
  - 熟练度：0-100
  - 复习次数
  - 正确次数
- 🏷️ **标签**：添加/删除标签
- 📄 **备注**：用户笔记
- 📍 **来源**：
  - 来源应用
  - 来源URL
  - 上下文
- ⏰ **时间**：
  - 创建时间
  - 更新时间
  - 上次复习
  - 下次复习

**编辑操作：**
- ✏️ **编辑**：修改翻译、添加笔记
- 🏷️ **添加标签**：输入标签名（回车添加）
- 🗑️ **删除标签**：选中标签 → 点击删除
- ❌ **删除词条**：点击删除按钮（软删除）

#### 3.2 统计标签页

**学习概览卡片：**
- 📚 **总词条**：词库中的总数量
- ➕ **今日新增**：今天新增的词条数
- 🔄 **待复习**：需要复习的词条数
- ✅ **已掌握**：熟练度>=80的词条数

**趋势图表：**

1. **每日新增词条（柱状图）**
   - 显示每天新增的词条数量
   - 最多显示最近14天
   - 鼠标悬停查看具体数值

2. **复习正确率（折线图）**
   - 显示每天复习的正确率百分比
   - 最多显示最近14天
   - 帮助评估学习效果

**详细数据表格：**
- 日期
- 新增词条数
- 复习次数
- 正确率
- 学习时长（分钟）

**时间范围筛选：**
- 最近7天
- 最近30天
- 最近90天
- 全部

**刷新数据：**
- 点击"刷新"按钮更新统计

---

### 4. 系统托盘

**托盘图标功能：**
- 🖼️ 显示程序图标
- 📱 右键弹出菜单

**右键菜单选项：**
1. **显示主窗口** - 打开主窗口
2. **切换剪贴板监听** - 开启/关闭剪贴板监听
3. **退出程序** - 完全关闭程序

**使用技巧：**
- 程序会最小化到托盘，不会完全关闭
- 双击托盘图标 = 显示主窗口
- 程序会在后台持续监听热键

---

## 高级功能

### 1. OCR 截图翻译

**功能说明：**
- 识别图片中的文字并翻译
- 适用于无法复制的文字（如图片、视频、扫描件）

**使用步骤：**
1. 按快捷键 `Ctrl+Shift+Q`
2. 屏幕变暗，出现选区工具
3. 鼠标拖动选择要识别的区域
4. 松开鼠标，自动识别并翻译
5. 翻译结果显示在浮动窗口

**注意事项：**
- ⚠️ 需要安装 PaddleOCR：`pip install paddleocr`
- ⚠️ 首次使用会下载模型（约100MB）
- ⚠️ 识别准确率受图片质量影响

**最佳实践：**
- ✅ 选择文字清晰的区域
- ✅ 尽量选择单一语言
- ✅ 避免选择过大区域
- ❌ 避免手写字体
- ❌ 避免艺术字体

---

### 2. 发音功能 (TTS)

**使用方法：**
1. 翻译完成后，点击浮动窗口的 📖 按钮
2. 自动播放语音
3. 支持多语言发音

**技术细节：**
- 使用 edge-tts 引擎
- 高质量语音合成
- 异步生成，不阻塞界面

**支持的语言：**
- 🇬🇧 英语 (en)
- 🇨🇳 中文 (zh)
- 🇯🇵 日语 (ja)
- 🇰🇷 韩语 (ko)
- 等等...

**配置选项：**
```toml
[features]
enable_tts = true           # 是否启用TTS
```

---

### 3. 智能翻译路由

**路由策略：**

```
输入文本
    ↓
语言检测
    ↓
是单词？
    ├─ 是 → 查询本地词典
    │       ├─ 找到 → 返回结果（快速）
    │       └─ 未找到 → AI翻译
    │
    └─ 否 → 直接AI翻译（短语/句子）
```

**本地词典优先：**
- ⚡ 毫秒级响应
- 📚 1000+常用单词
- 📖 包含音标、例句
- 🔄 自动降级到AI

**AI翻译特点：**
- 🧠 准确理解上下文
- 📝 自然流畅的翻译
- 🌐 支持多语言
- 💰 消耗API配额

**缓存机制：**
- 相同文本自动使用缓存
- 避免重复请求
- 节省API费用

---

### 4. 标签系统

**标签功能：**
- 🏷️ 给词条添加标签
- 📂 分类管理词条
- 🔍 按标签筛选

**标签操作：**

1. **添加标签**
   ```
   词条详情 → 标签列表 → 输入标签名 → 点击"添加"
   ```

2. **删除标签**
   ```
   词条详情 → 标签列表 → 选中标签 → 点击"删除"
   ```

3. **标签管理**
   - 每个词条可以有多个标签
   - 标签名支持中英文
   - 自动统计标签使用次数

**推荐标签：**
- 📚 **学科分类**：计算机、医学、法律、金融
- 📖 **词性**：名词、动词、形容词、副词
- 🎯 **难度**：简单、中等、困难
- 📅 **时间**：2025-11、项目A、课程B
- 🌟 **重要性**：重点、常用、专业术语

---

### 5. 收藏功能

**使用方式：**

**方式一：浮动窗口**
```
翻译后 → 点击 ⭐ 收藏按钮
```

**方式二：主窗口**
```
词条详情 → 勾选"收藏"
```

**收藏的作用：**
- ✅ 标记重要词条
- ✅ 方便快速找到
- ✅ 突出显示（可配置）

**查询收藏：**
```sql
-- 在数据库中查询收藏的词条
SELECT * FROM entries WHERE is_starred = 1;
```

---

### 6. 上下文捕获

**自动记录：**
- 📱 **来源应用**：哪个程序触发的翻译
- 🌐 **来源URL**：浏览器中的网页地址
- 📄 **上下文**：翻译时的周围文本

**使用场景：**
1. **追溯词源**
   - "这个词是在哪篇文章看到的？"
   - 查看词条详情 → 来源URL

2. **学习回顾**
   - "我在学习XX课程时查了哪些单词？"
   - 按来源应用筛选

3. **知识关联**
   - 查看词条的上下文
   - 更好地理解用法

**隐私保护：**
- 可以配置黑名单，排除特定应用
- 敏感信息不会被记录

**配置选项：**
```toml
[features]
enable_context_capture = true   # 是否启用上下文捕获

[blacklist.apps]
names = [
    "WeChat.exe",
    "QQ.exe",
    "*银行*"
]
```

---

## 设置说明

### 打开设置

```
主窗口 → 顶部工具栏 → ⚙️ 设置按钮
```

### 设置界面

#### 1. 应用设置

```toml
[app]
name = "TransLearn"        # 应用名称
version = "1.0.0"          # 版本号
language = "zh_CN"         # 界面语言
```

#### 2. 数据库设置

```toml
[database]
host = "localhost"         # MySQL主机
port = 3306                # 端口
user = "translearn"        # 用户名
password = "your_password" # 密码（敏感信息，不会显示）
database = "translearn"    # 数据库名
charset = "utf8mb4"        # 字符集
pool_size = 5              # 连接池大小
max_overflow = 10          # 最大溢出连接
pool_recycle = 3600        # 连接回收时间（秒）
```

#### 3. 热键设置

```toml
[hotkey]
translate = "ctrl+q"           # 划词翻译
open_main_window = "ctrl+shift+l"   # 打开主窗口
toggle_monitor = "ctrl+shift+t"     # 切换剪贴板监听
screenshot_ocr = "ctrl+shift+q"     # OCR截图翻译
```

**支持的按键：**
- 修饰键：`ctrl`, `shift`, `alt`, `win`
- 字母键：`a-z`
- 数字键：`0-9`
- 功能键：`f1-f12`

**注意事项：**
- ⚠️ 避免与系统热键冲突
- ⚠️ 避免与其他软件热键冲突
- ⚠️ 修改后需要重启程序

#### 4. 翻译设置

**AI翻译配置：**

```toml
[translation.ai]
provider = "openai"              # 提供商
api_key = "sk-xxx"               # API密钥
model = "gpt-3.5-turbo"          # 模型
base_url = ""                    # 自定义API地址（可选）
timeout = 10                     # 超时时间（秒）
max_retries = 3                  # 最大重试次数
```

**支持的提供商：**

1. **OpenAI**
   ```toml
   provider = "openai"
   model = "gpt-3.5-turbo"        # 或 gpt-4, gpt-4-turbo
   api_key = "sk-xxxxx"
   ```

2. **DashScope（阿里云）**
   ```toml
   provider = "dashscope"
   model = "qwen-turbo"           # 或 qwen-plus, qwen-max
   api_key = "sk-xxxxx"
   ```

3. **Ollama（本地）**
   ```toml
   provider = "ollama"
   model = "llama2"               # 或其他本地模型
   base_url = "http://localhost:11434"
   ```

**本地词典配置：**

```toml
[translation.local_dict]
enabled = true                              # 是否启用
dict_path = "data/dict/en-zh.json"          # 词典文件路径
fallback_to_ai = true                       # 未找到时降级到AI
```

#### 5. UI设置

```toml
[ui]
theme = "light"                 # 主题：light / dark

[ui.popup_window]
width = 400                     # 浮动窗口宽度
height = 300                    # 浮动窗口高度
opacity = 0.95                  # 不透明度（0-1）
auto_hide = true                # 是否自动隐藏
auto_hide_delay = 10000         # 自动隐藏延迟（毫秒）
always_on_top = true            # 是否置顶

[ui.main_window]
width = 900                     # 主窗口宽度
height = 700                    # 主窗口高度
remember_position = true        # 记住窗口位置
remember_size = true            # 记住窗口大小
```

#### 6. 功能开关

```toml
[features]
enable_clipboard_monitor = true     # 剪贴板监听
enable_tts = true                   # 发音功能
enable_context_capture = true       # 上下文捕获
enable_cache = true                 # 翻译缓存
enable_stats = true                 # 统计功能
```

#### 7. 学习与复习

```toml
[review]
algorithm = "sm2"                   # 复习算法：SM-2
initial_ease_factor = 2.5           # 初始难度系数
initial_interval = 1                # 初始间隔（天）
max_interval = 365                  # 最大间隔（天）
min_interval = 1                    # 最小间隔（天）
```

#### 8. 缓存设置

```toml
[cache]
enabled = true                      # 是否启用缓存
expire_days = 30                    # 缓存过期天数
max_entries = 10000                 # 最大缓存条目数
auto_clean = true                   # 自动清理过期缓存
```

#### 9. 黑名单

```toml
[blacklist]
enabled = true                      # 是否启用黑名单

[blacklist.apps]
names = [                           # 应用黑名单
    "WeChat.exe",
    "QQ.exe",
    "1Password.exe"
]

[blacklist.urls]
patterns = [                        # URL模式黑名单
    "*bank*",
    "*password*",
    "*admin*"
]
```

---

## 常见问题

### 1. 程序无法启动

**症状：**
- 双击run.bat无反应
- 命令行报错

**解决方法：**

1. **检查Python版本**
   ```bash
   python --version
   # 应该显示 Python 3.10 或更高
   ```

2. **检查依赖安装**
   ```bash
   pip list | findstr PyQt6
   pip list | findstr mysql
   ```

3. **查看日志文件**
   ```bash
   # 打开日志文件
   notepad data\logs\translearn_YYYYMMDD.log
   ```

4. **以管理员身份运行**
   - 右键 run.bat → 以管理员身份运行

---

### 2. 数据库连接失败

**症状：**
- 启动时报错：`Can't connect to MySQL server`
- 日志中显示数据库连接错误

**解决方法：**

1. **确认MySQL服务已启动**
   ```bash
   # Windows服务管理器
   services.msc
   # 查找 MySQL 服务，确保状态为"正在运行"
   ```

2. **检查配置文件**
   ```bash
   # 打开配置文件
   notepad data\config.toml
   
   # 确认以下配置正确：
   [database]
   host = "localhost"
   port = 3306
   user = "translearn"      # 用户名
   password = "你的密码"     # 密码
   database = "translearn"   # 数据库名
   ```

3. **测试数据库连接**
   ```bash
   mysql -h localhost -u translearn -p
   # 输入密码后应该能成功登录
   ```

4. **确认数据库已创建**
   ```sql
   SHOW DATABASES LIKE 'translearn';
   ```

---

### 3. 热键不生效

**症状：**
- 按 Ctrl+Q 没有反应
- 其他热键也无效

**解决方法：**

1. **检查是否与其他软件冲突**
   - 关闭其他使用相同热键的软件
   - 尝试修改热键配置

2. **以管理员身份运行**
   - 某些程序可能阻止热键监听
   - 以管理员身份运行可以解决

3. **检查热键监听是否启动**
   - 查看日志：`热键监听已启动`
   - 如果没有，说明启动失败

4. **修改热键配置**
   ```toml
   [hotkey]
   translate = "ctrl+alt+q"    # 改用 Ctrl+Alt+Q
   ```

---

### 4. 翻译失败

**症状：**
- 浮动窗口显示"翻译失败"
- 始终无法获取翻译结果

**解决方法：**

1. **检查网络连接**
   ```bash
   ping api.openai.com
   # 或
   ping dashscope.aliyuncs.com
   ```

2. **检查API密钥**
   - 确认API Key正确
   - 确认API Key有效（未过期）
   - 确认API Key有余额

3. **检查配置**
   ```toml
   [translation.ai]
   provider = "openai"          # 提供商名称
   api_key = "sk-xxxxx"         # API密钥
   model = "gpt-3.5-turbo"      # 模型名称
   ```

4. **查看详细日志**
   ```bash
   notepad data\logs\translearn_YYYYMMDD.log
   # 搜索 "翻译失败" 或 "error"
   ```

5. **尝试本地词典**
   - 如果是单词，会先查询本地词典
   - 确认词典文件存在：`data/dict/en-zh.json`

---

### 5. OCR功能不可用

**症状：**
- 按 Ctrl+Shift+Q 无反应
- 提示"OCR功能不可用"

**解决方法：**

1. **安装PaddleOCR**
   ```bash
   pip install paddleocr
   ```

2. **首次使用下载模型**
   - 首次使用会自动下载模型（约100MB）
   - 确保网络畅通
   - 等待下载完成

3. **检查日志**
   ```bash
   notepad data\logs\translearn_YYYYMMDD.log
   # 查找 "OCR" 相关错误
   ```

---

### 6. 发音无声音

**症状：**
- 点击发音按钮无声音
- 日志显示TTS错误

**解决方法：**

1. **确认edge-tts已安装**
   ```bash
   pip install edge-tts
   ```

2. **检查系统音量**
   - 确认系统音量未静音
   - 确认扬声器正常工作

3. **检查网络连接**
   - edge-tts需要联网
   - 确认能访问微软服务

4. **查看日志**
   ```bash
   notepad data\logs\translearn_YYYYMMDD.log
   # 搜索 "TTS" 或 "pronunciation"
   ```

---

### 7. 主窗口显示乱码

**症状：**
- 界面显示乱码或方块
- 中文无法正常显示

**解决方法：**

1. **检查系统编码**
   - Windows设置 → 时间和语言 → 语言
   - 确认系统语言为中文

2. **检查字体**
   - 确认系统安装了中文字体
   - 推荐：微软雅黑、宋体

3. **检查数据库编码**
   ```sql
   SHOW VARIABLES LIKE 'character%';
   -- 应该显示 utf8mb4
   ```

---

### 8. 程序占用CPU过高

**症状：**
- 任务管理器显示CPU占用很高
- 电脑运行变慢

**解决方法：**

1. **关闭剪贴板监听**
   - 按 Ctrl+Shift+T 关闭监听
   - 或在配置中禁用

2. **减少统计刷新频率**
   - 不要频繁打开统计页面

3. **清理数据库**
   ```sql
   -- 删除过期缓存
   DELETE FROM translation_cache WHERE expires_at < NOW();
   
   -- 删除已删除的词条
   DELETE FROM entries WHERE is_deleted = 1;
   ```

4. **检查后台进程**
   - 可能是OCR或TTS进程未关闭

---

## 技巧与窍门

### 1. 高效使用热键

**推荐热键配置：**
```toml
[hotkey]
translate = "ctrl+q"              # 常用功能，单手可按
open_main_window = "ctrl+shift+l"  # 较少使用，复杂点没关系
toggle_monitor = "ctrl+shift+t"    # 切换功能
screenshot_ocr = "ctrl+shift+s"    # OCR功能
```

**使用技巧：**
- 📌 把最常用的翻译功能设置为最简单的热键
- 📌 使用Shift组合键避免冲突
- 📌 记住常用热键，提高效率

---

### 2. 标签管理技巧

**推荐标签体系：**

```
├── 学科分类
│   ├── 计算机
│   ├── 医学
│   └── 法律
│
├── 学习来源
│   ├── 课程A
│   ├── 项目B
│   └── 书籍C
│
├── 掌握程度
│   ├── 已掌握
│   ├── 学习中
│   └── 待学习
│
└── 重要程度
    ├── 重点
    ├── 常用
    └── 了解即可
```

**标签命名规范：**
- ✅ 简短明确：`计算机` 而不是 `计算机相关专业术语`
- ✅ 统一风格：全部中文或全部英文
- ✅ 分级清晰：使用`-`连接：`计算机-前端-React`

---

### 3. 提升翻译质量

**优化翻译结果：**

1. **选择合适的模型**
   ```toml
   # 追求速度
   model = "gpt-3.5-turbo"
   
   # 追求质量
   model = "gpt-4-turbo"
   ```

2. **提供上下文**
   - 选择文本时包含前后句子
   - 帮助AI理解语境

3. **使用专业词典**
   - 导入专业领域词典
   - 放在 `data/dict/` 目录

---

### 4. 数据备份与迁移

**定期备份数据：**

```bash
# 导出数据库
mysqldump -u translearn -p translearn > backup_20251109.sql

# 导出配置文件
copy data\config.toml backup\config_20251109.toml

# 导出词典
copy data\dict\*.json backup\
```

**迁移到新电脑：**

```bash
# 1. 在新电脑安装程序
# 2. 导入数据库
mysql -u translearn -p translearn < backup_20251109.sql

# 3. 复制配置文件
copy backup\config_20251109.toml data\config.toml

# 4. 复制词典
copy backup\*.json data\dict\
```

---

### 5. 性能优化

**提升响应速度：**

1. **启用缓存**
   ```toml
   [cache]
   enabled = true
   expire_days = 30
   ```

2. **减少数据库查询**
   ```toml
   [database]
   pool_size = 10          # 增加连接池
   ```

3. **使用本地词典**
   - 常用单词走本地词典
   - 毫秒级响应

4. **定期清理数据**
   ```sql
   -- 清理过期缓存
   DELETE FROM translation_cache 
   WHERE expires_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
   ```

---

### 6. 学习方法建议

**有效学习流程：**

```
1. 阅读 → 2. 翻译 → 3. 收藏 → 4. 标签 → 5. 复习
    ↓         ↓         ↓         ↓         ↓
  遇到      理解      保存      分类      巩固
```

**复习计划：**
- 每天打开统计页面查看待复习词条
- 重点复习"学习中"标签的词条
- 已掌握的词条定期回顾

**进阶技巧：**
- 📚 导出词条制作Anki卡片
- 📝 在备注中添加个人理解
- 🔗 记录词条的来源链接
- 👥 分享标签体系给同学

---

## 附录

### A. 快捷键速查表

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl+Q` | 划词翻译 | 选中文本后按下 |
| `Ctrl+Shift+L` | 打开主窗口 | 显示词库和统计 |
| `Ctrl+Shift+T` | 切换剪贴板监听 | 开启/关闭自动翻译 |
| `Ctrl+Shift+Q` | OCR截图翻译 | 框选屏幕区域识别 |
| `Esc` | 关闭浮动窗口 | 隐藏翻译结果 |

### B. 配置文件模板

完整的配置文件模板请参考：`data/config.example.toml`

### C. 日志文件位置

- **路径**：`data/logs/`
- **命名**：`translearn_YYYYMMDD.log`
- **级别**：INFO, WARNING, ERROR
- **保留**：默认保留30天

### D. 数据库表结构

详细的数据库表结构请参考：`docs/DATABASE.md`

### E. API文档

内部API文档请参考：`docs/API.md`

### F. 架构设计

项目架构设计请参考：`docs/ARCHITECTURE.md`

---

## 获取帮助

### 1. 查看文档

- **快速开始**: `QUICKSTART.md`
- **使用指南**: `docs/USER_GUIDE.md`（本文档）
- **功能清单**: `docs/FEATURE_CHECKLIST.md`
- **完成总结**: `docs/FINAL_COMPLETION_SUMMARY.md`

### 2. 查看日志

```bash
# 打开最新日志文件
cd data\logs
dir /od
notepad translearn_最新日期.log
```

### 3. 问题反馈

如遇到问题，请提供以下信息：
- 操作系统版本
- Python版本
- MySQL版本
- 错误日志
- 复现步骤

---

## 更新日志

### v1.0.0 (2025-11-09)

**首次发布：**
- ✅ 核心翻译功能
- ✅ 词库管理
- ✅ 统计图表
- ✅ OCR识别
- ✅ 标签系统
- ✅ 发音功能

---

**文档版本**: 1.0.0  
**最后更新**: 2025-11-09  
**维护者**: TransLearn Team

---

© 2025 TransLearn. All rights reserved.

