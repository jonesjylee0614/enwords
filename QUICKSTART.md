# 🚀 快速开始

## 一、环境准备

### 必需软件

1. **Python 3.10+**
   - 下载: https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **MySQL 5.7+**
   - 下载: https://dev.mysql.com/downloads/mysql/
   - 或使用 XAMPP/WAMP

### 可选软件

- Git (用于克隆项目)
- Visual Studio Code (推荐编辑器)

## 二、安装步骤

### 方法一：自动安装（推荐）

```bash
# 1. 进入项目目录
cd translearn

# 2. 运行安装脚本
python scripts/setup_dev.py

# 3. 按照提示配置
```

### 方法二：手动安装

#### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

#### 步骤 2: 创建数据库

在 MySQL 中执行:

```sql
CREATE DATABASE translearn CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

或使用命令行:

```bash
mysql -u root -p < scripts/create_database.sql
```

#### 步骤 3: 配置应用

复制配置文件:

```bash
# Windows
copy data\config.example.toml data\config.toml

# Linux/Mac
cp data/config.example.toml data/config.toml
```

编辑 `data/config.toml`，修改以下配置:

```toml
[database]
host = "localhost"
port = 3306
user = "root"
password = "你的MySQL密码"
database = "translearn"

[translation.ai]
provider = "dashscope"  # 或 "openai"
api_key = "你的API密钥"  # 从 https://dashscope.console.aliyun.com/ 获取
```

#### 步骤 4: 初始化数据库

```bash
python scripts/init_database.py
```

看到 "数据库初始化完成!" 表示成功。

## 三、运行应用

### Windows

双击运行:
```
run.bat
```

或命令行:
```bash
python -m src
```

### Linux/Mac

```bash
python -m src
```

## 四、首次使用

### 1. 启动检查

启动后应该能看到:
- 系统托盘出现应用图标
- 控制台显示日志信息

### 2. 测试翻译

1. 打开任意应用（如浏览器、记事本）
2. 选中一段英文文本
3. 按 `Ctrl+Q`
4. 应该弹出翻译窗口

示例文本:
```
Hello world
```

### 3. 查看词库

1. 按 `Ctrl+Shift+L` 打开主窗口
2. 点击 "📚 词库" 标签
3. 查看翻译历史

### 4. 托盘菜单

右键点击托盘图标:
- 打开主窗口
- 退出应用

## 五、常见问题排查

### 问题 1: 启动失败

**错误**: "未找到模块 XXX"

**解决**:
```bash
pip install -r requirements.txt
```

---

**错误**: "数据库连接失败"

**解决**:
1. 确认 MySQL 已启动
2. 检查 `data/config.toml` 中的数据库配置
3. 确认数据库 `translearn` 已创建

---

**错误**: "配置文件不存在"

**解决**:
```bash
copy data\config.example.toml data\config.toml
```

### 问题 2: 热键不生效

**原因**: 快捷键冲突

**解决**:
1. 编辑 `data/config.toml`
2. 修改 `[hotkey]` 部分
3. 重启应用

### 问题 3: 翻译失败

**错误**: "API Key 未配置"

**解决**:
1. 编辑 `data/config.toml`
2. 配置 `[translation.ai]` 中的 `api_key`
3. 重启应用

---

**错误**: "翻译超时"

**解决**:
1. 检查网络连接
2. 增加超时时间（修改配置 `timeout = 30`）
3. 切换 AI 提供商

### 问题 4: 悬浮窗不显示

**检查**:
1. 查看控制台是否有错误
2. 检查是否被其他窗口遮挡
3. 查看日志: `data/logs/translearn_*.log`

## 六、获取 API Key

### DashScope (推荐，国内)

1. 访问: https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key
5. 复制 API Key 到配置文件

**优势**:
- 国内访问快
- 价格便宜
- 免费额度

### OpenAI (国际)

1. 访问: https://platform.openai.com/
2. 注册账号
3. 添加支付方式
4. 创建 API Key
5. 复制到配置文件

**注意**: 
- 需要国际信用卡
- 需要 VPN 访问

## 七、下一步

- 📖 阅读 [使用指南](docs/USAGE.md)
- 🏗️ 了解 [架构设计](docs/ARCHITECTURE.md)
- 💾 查看 [数据库文档](docs/DATABASE.md)
- 🔧 学习 [API 文档](docs/API.md)

## 八、开发模式

如果你想参与开发:

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 代码格式化
black src/

# 运行测试
pytest

# 查看帮助
python -m src --help
```

## 九、获取帮助

遇到问题?

1. 查看文档: `docs/` 目录
2. 查看日志: `data/logs/`
3. 提交 Issue: GitHub Issues
4. 查看示例: `docs/USAGE.md`

## 十、卸载

如需卸载:

1. 停止应用
2. 删除项目目录
3. (可选) 删除数据库:
   ```sql
   DROP DATABASE translearn;
   ```

---

**享受使用 TransLearn! 🎉**

