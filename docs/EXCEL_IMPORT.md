# Excel 词库导入指南

## 📋 功能说明

`import_from_excel.py` 脚本可以将 Excel 格式的词库导入到：
1. 本地词典（`data/dict/en-zh.json`）
2. MySQL 数据库（`translearn.entries` 表）

---

## 📊 Excel 文件格式要求

### 标准格式（推荐）

Excel 文件的**第一行**应该是列标题：

| word    | translation | pos  | pronunciation | example                   |
|---------|-------------|------|---------------|---------------------------|
| hello   | 你好        | int. | /həˈloʊ/      | Hello, how are you?       |
| world   | 世界        | n.   | /wɜːrld/      | The world is beautiful.   |
| computer| 计算机      | n.   | /kəmˈpjuːtər/ | I bought a new computer.  |

**列说明**：
- **word** (必需): 英文单词
- **translation** (必需): 中文翻译
- **pos** (可选): 词性（如 n., v., adj., adv. 等）
- **pronunciation** (可选): 音标
- **example** (可选): 例句

### 简化格式（没有列标题）

如果 Excel 文件没有列标题，脚本会自动使用列索引：
- **第 1 列**: 英文单词（必需）
- **第 2 列**: 中文翻译（必需）
- **第 3 列**: 词性（可选）
- **第 4 列**: 音标（可选）
- **第 5 列**: 例句（可选）

---

## 🚀 使用方法

### 1. 安装依赖

```bash
cd d:\WorkSpace\code\2025\enwords
pip install openpyxl pandas
```

### 2. 准备 Excel 文件

下载或创建一个 Excel 文件（`.xlsx` 格式），确保格式符合上述要求。

### 3. 执行导入

#### 基本用法（导入所有内容）

```bash
python scripts/import_from_excel.py "path/to/your/dictionary.xlsx"
```

#### 只更新本地词典（不保存到数据库）

```bash
python scripts/import_from_excel.py "dictionary.xlsx" --no-db
```

#### 只保存到数据库（不更新本地词典）

```bash
python scripts/import_from_excel.py "dictionary.xlsx" --no-local
```

#### 从指定行开始导入

```bash
# 从第 101 行开始导入（跳过前 100 行）
python scripts/import_from_excel.py "dictionary.xlsx" --start 100
```

#### 限制导入数量

```bash
# 只导入前 1000 行
python scripts/import_from_excel.py "dictionary.xlsx" --max 1000
```

#### 分批导入大文件

```bash
# 导入第 1-1000 行
python scripts/import_from_excel.py "dictionary.xlsx" --start 0 --max 1000

# 导入第 1001-2000 行
python scripts/import_from_excel.py "dictionary.xlsx" --start 1000 --max 1000

# 导入第 2001-3000 行
python scripts/import_from_excel.py "dictionary.xlsx" --start 2000 --max 1000
```

---

## 📝 示例

### 示例 1：导入小型词库

```bash
python scripts/import_from_excel.py "data/my_words.xlsx"
```

**输出**：
```
INFO | 开始导入 Excel 词库: data/my_words.xlsx
INFO | Excel 文件读取成功，共 500 行
INFO | 有效词条: 498 个
INFO | 现有词典: 20 个词条
SUCCESS | 本地词典已更新: data\dict\en-zh.json
INFO | 总词条数: 518
INFO | 开始保存到数据库...
INFO | 已保存 100 条...
INFO | 已保存 200 条...
...
SUCCESS | 数据库保存完成！
INFO |   - 新增: 498 条
INFO |   - 跳过（已存在）: 0 条
INFO |   - 失败: 0 条
SUCCESS | 🎉 导入成功！
```

### 示例 2：导入大型词库（分批）

```bash
# 第一批：前 5000 行
python scripts/import_from_excel.py "large_dict.xlsx" --max 5000

# 第二批：第 5001-10000 行
python scripts/import_from_excel.py "large_dict.xlsx" --start 5000 --max 5000
```

---

## 🎯 功能特点

### 1. 自动去重

- **本地词典**: 相同单词的新翻译会覆盖旧翻译
- **数据库**: 跳过已存在的单词

### 2. 数据清理

- 自动删除空行
- 自动删除重复的单词（保留第一个）
- 自动去除前后空格
- 单词统一转为小写

### 3. 智能列识别

- 优先使用列标题（word, translation）
- 如果没有标题，自动使用列索引
- 支持可选列（词性、音标、例句）

### 4. 进度显示

- 每 100 条显示一次进度
- 显示导入统计（新增、跳过、失败）

### 5. 错误处理

- 单个词条失败不影响其他词条
- 错误超过 10 个自动终止

---

## 📦 推荐的词库来源

### 1. GitHub 开源词库

- [ECDICT](https://github.com/skywind3000/ECDICT) - 75万+ 词条
- [CET4/CET6 词库](https://github.com/mahavivo/english-wordlists)
- [TOEFL/IELTS 词库](https://github.com/kajweb/dict)

### 2. 自制词库

使用 Excel 创建：
1. 打开 Excel
2. 第一行输入列标题：`word`, `translation`, `pos`, `pronunciation`, `example`
3. 从第二行开始输入词条
4. 保存为 `.xlsx` 格式

### 3. 在线词库

从在线词典网站导出，常见格式：
- CSV → 用 Excel 打开并保存为 `.xlsx`
- JSON → 用脚本转换为 Excel

---

## ⚠️ 注意事项

### 1. Excel 文件大小

- 建议单个文件不超过 50,000 行
- 大文件请使用 `--max` 参数分批导入

### 2. 内存使用

- 导入大型词库时，pandas 会占用较多内存
- 建议分批导入，每批 5000-10000 行

### 3. 数据库性能

- 第一次导入时，数据库会自动创建索引
- 导入过程中，数据库连接会保持打开
- 如果导入中断，已保存的词条不会丢失

### 4. 本地词典 vs 数据库

**本地词典**（`en-zh.json`）：
- ✅ 查询速度极快（内存中）
- ✅ 支持即时翻译
- ❌ 只能存储基本信息（单词、翻译、词性、音标）
- ❌ 不支持复杂查询

**数据库**（MySQL）：
- ✅ 支持复杂查询和统计
- ✅ 支持更多字段（熟练度、收藏、标签等）
- ✅ 支持学习记录
- ❌ 查询速度较慢（需要访问数据库）

**建议**：
- 常用词（如 CET4/CET6）→ 导入本地词典 + 数据库
- 不常用词 → 只导入数据库
- 学习中的词 → 手动添加到数据库（带学习记录）

---

## 🔧 故障排除

### 问题 1：找不到模块

```
ModuleNotFoundError: No module named 'openpyxl'
```

**解决**：
```bash
pip install openpyxl pandas
```

### 问题 2：Excel 文件无法读取

```
ERROR | 读取 Excel 文件失败: ...
```

**解决**：
- 确保文件是 `.xlsx` 格式（不是 `.xls` 或 `.csv`）
- 确保文件没有被其他程序打开
- 尝试用 Excel 重新保存一次

### 问题 3：数据库连接失败

```
ERROR | 保存到数据库失败: ...
```

**解决**：
- 确保 MySQL 服务正在运行
- 检查 `data/config.toml` 中的数据库配置
- 运行 `python scripts/init_database.py` 初始化数据库

### 问题 4：内存不足

```
MemoryError: ...
```

**解决**：
- 使用 `--max` 参数分批导入
- 减少每批的数量（如 1000 或 2000）

---

## 📊 导入后验证

### 1. 检查本地词典

```bash
# Windows PowerShell
(Get-Content data\dict\en-zh.json | ConvertFrom-Json).Count

# Linux/Mac
jq 'length' data/dict/en-zh.json
```

### 2. 检查数据库

```bash
python
```

```python
from src.data.repository import EntryRepository

repo = EntryRepository()
count = repo.get_total_count()
print(f"数据库中共有 {count} 个词条")
```

### 3. 测试翻译

1. 启动程序：`run.bat`
2. 选中一个导入的单词
3. 按 `Ctrl+5`
4. 查看翻译是否正确

---

## 🎉 完成！

现在你可以：
1. ✅ 导入任意 Excel 格式的词库
2. ✅ 自动更新本地词典和数据库
3. ✅ 分批导入大型词库
4. ✅ 灵活控制导入范围

开始享受强大的本地词典吧！📚✨

