## 小红书话题笔记热度排行爬虫 🕷️

一个用于爬取小红书话题下笔记热度排行数据的爬虫项目。可以自动获取指定话题下的笔记热度排行，包括发布时间、点赞数、评论数、收藏数等数据。

### 功能特性 ✨

- 📊 **自动爬取话题排行** - 获取小红书指定话题下的笔记热度排行
- 💾 **数据持久化** - 使用 SQLite 数据库存储爬取的数据
- 🌐 **免费代理支持** - 自动从多个免费代理源获取代理，轮换使用
- 🔄 **反爬虫处理** - 集成反爬虫机制，包括随机延迟、头部伪装等
- 📈 **数据分析** - 提供数据查询和统计功能
- 📁 **导出功能** - 支持将数据导出为 JSON 格式
- ⚙️ **配置灵活** - 支持通过环境变量自定义各项配置

### 数据字段 📋

爬虫会为每条笔记记录以下信息：

- **笔记ID** - 小红书笔记的唯一标识
- **标题** - 笔记标题
- **内容** - 笔记描述/摘要
- **作者** - 笔记发布者
- **发布时间** - 笔记发布时间
- **点赞数** - 获赞数
- **评论数** - 评论总数
- **收藏数** - 收藏总数
- **分享数** - 分享总数
- **URL** - 笔记链接

### 安装指南 🚀

#### 前置条件

- Python 3.8+
- pip (Python 包管理器)

#### 步骤

1. **克隆仓库**
```bash
git clone https://github.com/arlenheting-byte/xiaohongshu-topic-scraper.git
cd xiaohongshu-topic-scraper
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装浏览器驱动**
```bash
playwright install chromium
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件根据需要调整配置
```

### 使用指南 📖

#### 基本用法

爬取单个话题：
```bash
python main.py -t "穿搭"
```

爬取多个话题：
```bash
python main.py -t "穿搭" "护肤" "美食"
```

#### 高级用法

不使用代理（在某些环境下可能更快）：
```bash
python main.py -t "穿搭" --no-proxy
```

启用详细日志：
```bash
python main.py -t "穿搭" -v
```

#### 查询数据

使用 `query.py` 脚本查询和分析数据：

```python
from query import DataAnalyzer

analyzer = DataAnalyzer()

# 获取今日热门笔记
top_notes = analyzer.get_today_top_notes('穿搭', limit=10)

# 获取话题统计数据
stats = analyzer.get_topic_stats('穿搭')

# 对比多个话题
comparison = analyzer.compare_topics(['穿搭', '护肤', '美食'])

# 导出为 JSON
analyzer.export_to_json('穿搭', 'export_穿搭.json')
```

### 配置说明 ⚙️

编辑 `.env` 文件配置参数：

```env
# 数据库
DATABASE_PATH=xiaohongshu_data.db

# 爬虫设置
HEADLESS=True              # 无头浏览器模式
TIMEOUT=30                 # 请求超时时间（秒）
RETRY_TIMES=3              # 重试次数

# 代理设置
USE_PROXY=True             # 是否使用代理
PROXY_TIMEOUT=10           # 代理超时时间（秒）

# 日志
LOG_LEVEL=INFO             # 日志级别：DEBUG, INFO, WARNING, ERROR
```

### 项目结构 📁

```
xiaohongshu-topic-scraper/
├── main.py                # 主入口文件
├── scraper.py             # 爬虫核心模块
├── database.py            # 数据库操作模块
├── proxy_manager.py       # 代理管理模块
├── query.py               # 数据查询分析模块
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例
├── .gitignore             # Git 忽略文件
└── README.md              # 本文件
```

### 数据库结构 🗄️

#### notes 表
存储爬取的笔记信息

```sql
CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    title TEXT,
    content TEXT,
    author TEXT,
    publish_time TIMESTAMP,
    likes_count INTEGER,
    comments_count INTEGER,
    collections_count INTEGER,
    shares_count INTEGER,
    url TEXT,
    scraped_at TIMESTAMP
)
```

#### daily_ranking 表
存储每日排行数据

```sql
CREATE TABLE daily_ranking (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL,
    note_id TEXT NOT NULL,
    rank_position INTEGER,
    likes_count INTEGER,
    comments_count INTEGER,
    collections_count INTEGER,
    publish_time TIMESTAMP,
    scraped_date DATE,
    scraped_at TIMESTAMP
)
```

#### topics 表
记录追踪的话题

```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    topic_name TEXT UNIQUE,
    created_at TIMESTAMP,
    last_scraped_at TIMESTAMP
)
```

### 代理管理 🌐

项目集成了免费代理支持，自动从以下源获取代理：

1. **proxy-list.download** - 提供免费代理列表
2. **sslproxies.org** - SSL 代理列表
3. **GitHub proxy-list** - 社区维护的代理列表

代理会自动轮换使用，提高成功率。

### 注意事项 ⚠️

1. **遵守法律法规** - 请确保爬虫行为符合当地法律和小红书服务条款
2. **频率限制** - 建议设置适当延迟避免被限流
3. **代理质量** - 免费代理稳定性有限，可能需要多次重试
4. **隐私保护** - 不要爬取或存储用户隐私信息
5. **IP 限制** - 频繁请求可能导致 IP 被暂时限制

### 常见问题 ❓

**Q: 爬虫运行时出现 "No proxies available" 错误？**
A: 可能是代理源暂时不可用。尝试使用 `--no-proxy` 参数直接连接，或稍后重试。

**Q: 爬虫速度很慢？**
A: 这是正常的，因为要等待页面加载和解析。可以调整 `TIMEOUT` 参数或在配置中禁用代理。

**Q: 数据不完整或缺失？**
A: 小红书的页面结构可能发生了变化。请更新爬虫或检查 HTML 解析逻辑。

**Q: 如何定期运行爬虫？**
A: 可以使用系统的定时任务：
   - Linux/Mac: `crontab -e`
   - Windows: 任务计划程序

### 贡献指南 🤝

欢迎提交 Issue 和 Pull Request！

### 许可证 📄

MIT License

### 免责声明 ⚖️

本项目仅供学习和研究使用。使用本项目进行的任何爬虫活动应遵守相关法律法规和网站服务条款。作者对因使用本项目而造成的任何损害不承担责任。

### 更新日志 📝

**v1.0.0** (2026-05-22)
- 初始版本发布
- 实现基本爬虫功能
- 集成免费代理支持
- 完成数据库设计
- 提供数据查询接口

### 联系方式 📧

如有问题或建议，欢迎提交 Issue！
