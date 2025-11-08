# 数据库设计文档

## 概述

TransLearn 使用 MySQL 5.7+ 作为数据存储，通过 SQLAlchemy ORM 进行数据访问。

## 数据库配置

### 创建数据库

```sql
CREATE DATABASE translearn CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 配置连接

在 `data/config.toml` 中配置:

```toml
[database]
host = "localhost"
port = 3306
user = "root"
password = "your_password"
database = "translearn"
charset = "utf8mb4"
pool_size = 5
max_overflow = 10
pool_recycle = 3600
```

## 数据表结构

### 1. entries - 词条表

存储所有翻译过的词条。

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| source_text | TEXT | 原文 |
| translation | TEXT | 翻译 |
| source_lang | VARCHAR(10) | 源语言 |
| target_lang | VARCHAR(10) | 目标语言 |
| entry_type | VARCHAR(20) | 类型(word/phrase/sentence/paragraph) |
| context | TEXT | 上下文 |
| source_app | VARCHAR(100) | 来源应用 |
| source_url | VARCHAR(500) | 来源URL |
| familiarity | INT | 熟悉度(0-5) |
| review_count | INT | 复习次数 |
| correct_count | INT | 答对次数 |
| last_review | DATETIME | 上次复习时间 |
| next_review | DATETIME | 下次复习时间 |
| ease_factor | FLOAT | SM-2难度系数 |
| interval | INT | SM-2间隔天数 |
| tags | TEXT | 标签(JSON) |
| notes | TEXT | 用户笔记 |
| translator_type | VARCHAR(50) | 翻译器类型 |
| translation_time | FLOAT | 翻译耗时(秒) |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | BOOLEAN | 软删除标记 |

**索引:**
- UNIQUE(source_text, source_lang, target_lang)
- INDEX(created_at)
- INDEX(next_review)
- INDEX(familiarity)
- INDEX(source_text) - 限长100字符

### 2. tags - 标签表

存储自定义标签。

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| name | VARCHAR(50) | 标签名(唯一) |
| color | VARCHAR(20) | 颜色 |
| icon | VARCHAR(50) | 图标 |
| created_at | DATETIME | 创建时间 |

### 3. daily_stats - 每日统计表

记录每日学习数据。

| 字段 | 类型 | 说明 |
|-----|------|------|
| date | DATE | 日期(主键) |
| new_words | INT | 新词数 |
| reviews | INT | 复习数 |
| study_time | INT | 学习时长(秒) |
| translation_count | INT | 翻译次数 |
| ai_calls | INT | AI调用次数 |
| ai_tokens | INT | AI消耗tokens |

### 4. translation_cache - 翻译缓存表

缓存翻译结果。

| 字段 | 类型 | 说明 |
|-----|------|------|
| cache_key | VARCHAR(64) | 缓存键(MD5,主键) |
| source_text | TEXT | 原文 |
| translation | TEXT | 翻译 |
| translator_type | VARCHAR(50) | 翻译器类型 |
| created_at | DATETIME | 创建时间 |
| expires_at | DATETIME | 过期时间 |
| hit_count | INT | 命中次数 |

**索引:**
- INDEX(expires_at)

### 5. settings - 配置表

存储用户配置。

| 字段 | 类型 | 说明 |
|-----|------|------|
| key | VARCHAR(100) | 配置键(主键) |
| value | TEXT | 配置值 |
| updated_at | DATETIME | 更新时间 |

### 6. blacklist - 黑名单表

存储不监听的应用。

| 字段 | 类型 | 说明 |
|-----|------|------|
| app_name | VARCHAR(100) | 应用名(主键) |
| reason | VARCHAR(200) | 原因 |
| created_at | DATETIME | 创建时间 |

## 初始化

运行初始化脚本:

```bash
python scripts/init_database.py
```

## 备份与恢复

### 备份

```bash
mysqldump -u root -p translearn > backup.sql
```

### 恢复

```bash
mysql -u root -p translearn < backup.sql
```

## 性能优化

1. **连接池**: 使用 SQLAlchemy 连接池，避免频繁创建连接
2. **索引优化**: 为常查询字段建立索引
3. **批量操作**: 使用批量插入/更新减少数据库交互
4. **缓存机制**: 翻译结果缓存，减少重复查询
5. **定期清理**: 定期清理过期缓存和软删除数据

## 注意事项

1. 使用 utf8mb4 字符集支持 emoji 和特殊字符
2. 时间字段使用 DATETIME，应用层处理时区
3. 使用软删除保留数据历史
4. 定期备份数据库

