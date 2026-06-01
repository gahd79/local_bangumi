# 本地bangumi

## 起因
5月28日知名acgn网站bangumi被墙了。本人无意去讨论被墙的原因，但这让我认识到网络在便捷的同时又是如此的脆弱，所以有了把bangumi搬到本地的想法

## 主要想实现的功能
1. 能够进行acgn信息的查询，筛选
2. 能够记录用户的观看信息

## 实现的手段
1. bangumi官方每周都会在github更新wiki信息，这可以作为本地的信息来源
2. 至于记录，应该很简单

---

## 详细开发方案

### 一、技术选型

#### 后端技术栈
- **语言**: Python 3.10+
- **Web框架**: FastAPI (高性能、异步支持、自动生成API文档)
- **数据库**: SQLite (轻量级，适合个人项目) + SQLAlchemy ORM
- **数据解析**: JSON Lines格式解析 (处理.jsonlines文件)
- **Wiki语法解析**: wiki-parser-py (解析infobox的wiki原始字符串)
- **定时任务**: APScheduler (定期从GitHub同步数据)
- **HTTP客户端**: httpx (异步请求GitHub API)
- **数据处理**: pandas (可选，用于大规模数据处理)

#### 前端技术栈
- **框架**: Vue 3 + Vite
- **UI组件库**: Element Plus (丰富的组件，适合后台管理)
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP请求**: Axios

#### 开发工具
- **代码规范**: Black (Python), ESLint + Prettier (JavaScript)
- **版本控制**: Git
- **依赖管理**: Poetry (Python), npm/pnpm (Node.js)

---

### 二、项目结构设计

```
local_bangumi/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── config.py          # 配置文件
│   │   ├── database.py        # 数据库连接和会话管理
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── anime.py       # 动画模型
│   │   │   ├── game.py        # 游戏模型
│   │   │   ├── novel.py       # 小说模型
│   │   │   ├── comic.py       # 漫画模型
│   │   │   └── user_record.py # 用户观看记录模型
│   │   ├── schemas/           # Pydantic数据验证模式
│   │   │   ├── __init__.py
│   │   │   ├── anime.py
│   │   │   ├── game.py
│   │   │   ├── novel.py
│   │   │   ├── comic.py
│   │   │   └── user_record.py
│   │   ├── api/               # API路由
│   │   │   ├── __init__.py
│   │   │   ├── anime.py       # 动画相关API
│   │   │   ├── game.py        # 游戏相关API
│   │   │   ├── novel.py       # 小说相关API
│   │   │   ├── comic.py       # 漫画相关API
│   │   │   └── records.py     # 用户记录API
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── data_sync.py   # 数据同步服务(从GitHub获取)
│   │   │   ├── search.py      # 搜索服务
│   │   │   └── record_manager.py # 记录管理服务
│   │   ├── utils/             # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── github_fetcher.py # GitHub数据获取
│   │   │   └── parser.py      # YAML数据解析器
│   │   └── scheduler/         # 定时任务
│   │       ├── __init__.py
│   │       └── sync_scheduler.py # 数据同步调度器
│   ├── tests/                 # 测试文件
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_services.py
│   ├── requirements.txt       # Python依赖
│   ├── pyproject.toml         # Poetry配置
│   └── .env.example           # 环境变量示例
│
├── frontend/                  # 前端代码
│   ├── src/
│   │   ├── main.js            # 应用入口
│   │   ├── App.vue            # 根组件
│   │   ├── router/            # 路由配置
│   │   │   └── index.js
│   │   ├── stores/            # Pinia状态管理
│   │   │   ├── anime.js
│   │   │   ├── game.js
│   │   │   └── records.js
│   │   ├── views/             # 页面组件
│   │   │   ├── Home.vue       # 首页
│   │   │   ├── AnimeList.vue  # 动画列表页
│   │   │   ├── GameList.vue   # 游戏列表页
│   │   │   ├── NovelList.vue  # 小说列表页
│   │   │   ├── ComicList.vue  # 漫画列表页
│   │   │   ├── Search.vue     # 搜索页
│   │   │   └── MyRecords.vue  # 我的观看记录
│   │   ├── components/        # 通用组件
│   │   │   ├── Navbar.vue     # 导航栏
│   │   │   ├── Sidebar.vue    # 侧边栏
│   │   │   ├── ItemCard.vue   # 项目卡片组件
│   │   │   ├── SearchBar.vue  # 搜索框组件
│   │   │   └── RecordForm.vue # 记录表单组件
│   │   ├── api/               # API调用封装
│   │   │   ├── request.js     # Axios实例配置
│   │   │   ├── anime.js
│   │   │   ├── game.js
│   │   │   ├── novel.js
│   │   │   ├── comic.js
│   │   │   └── records.js
│   │   ├── utils/             # 工具函数
│   │   │   └── helpers.js
│   │   └── assets/            # 静态资源
│   │       ├── styles/        # 全局样式
│   │       └── images/        # 图片资源
│   ├── public/                # 公共资源
│   ├── index.html             # HTML模板
│   ├── package.json           # Node.js依赖
│   ├── vite.config.js         # Vite配置
│   └── .eslintrc.js           # ESLint配置
│
├── data/                      # 数据存储目录
│   ├── bangumi.db             # SQLite数据库文件
│   ├── cache/                 # 缓存目录
│   │   └── github_wiki/       # GitHub Wiki缓存
│   └── logs/                  # 日志目录
│       └── app.log
│
├── scripts/                   # 脚本文件
│   ├── init_db.py             # 数据库初始化脚本
│   ├── sync_data.py           # 手动数据同步脚本
│   └── backup_db.py           # 数据库备份脚本
│
├── docs/                      # 文档目录
│   ├── API.md                 # API文档
│   ├── DEVELOPMENT.md         # 开发指南
│   └── DEPLOYMENT.md          # 部署指南
│
├── docker-compose.yml         # Docker编排文件
├── Dockerfile.backend         # 后端Docker镜像
├── Dockerfile.frontend        # 前端Docker镜像
├── .gitignore                 # Git忽略文件
└── README.md                  # 项目说明文档
```

---

### 三、核心功能模块设计

#### 1. 数据同步模块 (Data Sync Service)

**功能描述**:
- 定期从Bangumi官方GitHub Archive仓库获取导出数据
- 解析JSON Lines格式的subject.jsonlines文件
- 解析infobox字段的Wiki原始字符串为结构化数据
- 将数据转换为结构化数据并存入数据库
- 增量更新机制，避免重复数据

**实现要点**:
- 从 `https://github.com/bangumi/Archive/releases/tag/archive` 下载最新数据
- 解析 `./aux/latest.json` 获取最新的导出文件地址
- 重点处理 `subject.jsonlines` 文件（每行一个JSON对象）
- 使用 `wiki-parser-py` 解析infobox字段
- 支持全量同步和增量同步两种模式
- 错误重试机制和网络异常处理
- 同步进度和状态监控

**数据来源**:
- Bangumi Archive: `https://github.com/bangumi/Archive`
- 每周三凌晨五点(GMT+8)更新
- 主要数据文件: `subject.jsonlines` (条目数据)
- 辅助数据: `episode.jsonlines`, `person.jsonlines`, `character.jsonlines` 等

**Subject数据结构**:
```
{
    "id": 1,                    # 条目ID
    "type": 2,                  # 作品类型: 1漫画, 2动画, 3音乐, 4游戏, 6三次元
    "name": "...",              # 条目名
    "name_cn": "...",           # 条目简体中文名
    "infobox": "...",           # 原始wiki字符串(需要解析)
    "platform": 2,              # 平台: TV/剧场版/OVA等
    "summary": "...",           # 条目简介
    "nsfw": false,              # 是否成人内容
    "date": "2024-01-01",       # 发行日期
    "favorite": {...},          # 收藏统计
    "series": false,            # 是否为系列作品
    "tags": [...],              # 标签列表
    "score": 7.5,               # 评分
    "score_details": {...},     # 评分分布详情
    "rank": 100,                # 类别内排名
    "meta_tags": [...]          # 公共标签(2025-04-18起)
}
```

**Infobox解析示例**:
```
# 原始infobox字符串:
# {{Infobox animedetail
# |中文名 = 星际牛仔
# |别名 = Cowboy Bebop
# |话数 = 26
# |放送开始 = 1998年4月3日
# }}

# 解析后:
{
    "中文名": "星际牛仔",
    "别名": "Cowboy Bebop",
    "话数": "26",
    "放送开始": "1998年4月3日"
}
```

**关联数据处理**:
- Subject-relations: 条目之间的关联(续作、前传、外传等)
- Subject-characters: 条目与角色的关联(主角、配角、客串)
- Subject-persons: 条目与人物的关联(STAFF信息)
- Episode: 章节/剧集信息(正篇、OP、ED等)

**UserRecord (用户记录)**:
```python
- id: 主键
- user_id: 用户ID(预留多用户支持)
- item_id: 条目ID
- item_type: 条目类型(anime/game/novel/comic)
- status: 观看状态(想看/在看/看过/搁置/抛弃)
- progress: 进度(看到第几集/章)
- rating: 个人评分(1-10)
- comment: 评论
- start_date: 开始日期
- finish_date: 完成日期
- created_at: 创建时间
- updated_at: 更新时间
```

#### 2. 数据模型设计 (Database Models)

**Subject (条目 - 统一存储所有类型)**:
```
- id: 主键
- bangumi_id: Bangumi唯一ID (索引)
- type: 作品类型 (1漫画, 2动画, 3音乐, 4游戏, 6三次元) (索引)
- name: 原始名称
- name_cn: 中文名称 (索引)
- name_en: 英文名称
- infobox_raw: 原始wiki字符串
- infobox_parsed: 解析后的结构化数据 (JSON格式)
- platform: 平台类型 (TV/剧场版/OVA等)
- summary: 简介
- nsfw: 是否成人内容
- date: 发行日期 (索引)
- series: 是否为系列作品
- tags: 标签列表 (JSON格式)
- meta_tags: 公共标签 (JSON格式)
- score: 评分 (索引)
- score_details: 评分分布详情 (JSON格式)
- rank: 类别内排名
- favorite_count: 收藏总数
- want_count: 想看数
- doing_count: 在看数
- done_count: 看过数
- on_hold_count: 搁置数
- dropped_count: 抛弃数
- created_at: 创建时间
- updated_at: 更新时间 (索引)
```

**Episode (章节/剧集)**:
```
- id: 主键
- bangumi_id: Bangumi章节ID
- subject_id: 所属条目ID (外键, 索引)
- name: 章节名称
- name_cn: 中文名称
- description: 章节介绍
- airdate: 播出日期 (索引)
- disc: 光盘编号
- duration: 播放时长
- sort: 排序号(第几集)
- type: 类型 (0正篇, 1特别篇, 2OP, 3ED, 4Trailer, 5MAD, 6其他)
- created_at: 创建时间
- updated_at: 更新时间
```

**Person (人物/STAFF)**:
```
- id: 主键
- bangumi_id: Bangumi人物ID
- name: 人物名称
- type: 类型 (1个人, 2公司, 3组合)
- career: 职业
- infobox_raw: 原始wiki字符串
- infobox_parsed: 解析后的数据 (JSON格式)
- summary: 简介
- comments_count: 评论数
- collects_count: 收藏数
- created_at: 创建时间
- updated_at: 更新时间
```

**Character (角色)**:
```
- id: 主键
- bangumi_id: Bangumi角色ID
- name: 角色名称
- role: 角色类型 (1角色, 2机体, 3组织等)
- infobox_raw: 原始wiki字符串
- infobox_parsed: 解析后的数据 (JSON格式)
- summary: 简介
- comments_count: 评论数
- collects_count: 收藏数
- created_at: 创建时间
- updated_at: 更新时间
```

**SubjectRelation (条目关联)**:
```
- id: 主键
- subject_id: 主条目ID (外键, 索引)
- relation_type: 关联类型 (续作/前传/外传/同系列等)
- related_subject_id: 关联条目ID (外键, 索引)
- order: 排序
- created_at: 创建时间
```

**SubjectCharacter (条目-角色关联)**:
```
- id: 主键
- subject_id: 条目ID (外键, 索引)
- character_id: 角色ID (外键, 索引)
- type: 角色类型 (1主角, 2配角, 3客串)
- order: 排序
- created_at: 创建时间
```

**SubjectPerson (条目-人物关联)**:
```
- id: 主键
- subject_id: 条目ID (外键, 索引)
- person_id: 人物ID (外键, 索引)
- position: 职位 (导演/编剧/作画等)
- appear_eps: 参与章节 (JSON格式, 2025-09-29起)
- created_at: 创建时间
```

**PersonCharacter (人物-角色关联/CV关系)**:
```
- id: 主键
- person_id: 人物ID (外键, 索引)
- subject_id: 条目ID (外键, 索引)
- character_id: 角色ID (外键, 索引)
- summary: 概要说明
- created_at: 创建时间
```

**UserRecord (用户记录)**:
```
- id: 主键
- user_id: 用户ID(预留多用户支持) (索引)
- subject_id: 条目ID (外键, 索引)
- status: 观看状态 (想看/在看/看过/搁置/抛弃) (索引)
- progress: 进度(看到第几集)
- rating: 个人评分(1-10)
- comment: 评论
- start_date: 开始日期
- finish_date: 完成日期
- created_at: 创建时间
- updated_at: 更新时间
```

#### 3. API接口设计 (RESTful API)

**条目相关API** (统一接口，通过type参数区分):
- `GET /api/subjects` - 获取条目列表(支持分页、筛选、类型过滤)
  - 参数: type(2动画/1漫画/4游戏等), page, limit, sort, order
- `GET /api/subjects/{id}` - 获取单个条目详情(包含关联的角色、人物、剧集等)
- `GET /api/subjects/search` - 搜索条目
  - 参数: q(关键词), type, tags, year_range, score_range
- `GET /api/subjects/{id}/episodes` - 获取条目的剧集列表
- `GET /api/subjects/{id}/characters` - 获取条目的角色列表
- `GET /api/subjects/{id}/persons` - 获取条目的人物(STAFF)列表
- `GET /api/subjects/{id}/relations` - 获取条目的关联条目
- `GET /api/subjects/tags` - 获取所有标签及统计
- `GET /api/subjects/stats` - 获取统计数据(各类型数量、热门条目等)

**剧集相关API**:
- `GET /api/episodes` - 获取剧集列表
- `GET /api/episodes/{id}` - 获取单个剧集详情

**人物相关API**:
- `GET /api/persons` - 获取人物列表
- `GET /api/persons/{id}` - 获取单个人物详情
- `GET /api/persons/search` - 搜索人物

**角色相关API**:
- `GET /api/characters` - 获取角色列表
- `GET /api/characters/{id}` - 获取单个角色详情
- `GET /api/characters/search` - 搜索角色

**用户记录API**:
- `GET /api/records` - 获取用户记录列表
  - 参数: status(想看/在看/看过等), type(条目类型), page, limit
- `POST /api/records` - 添加观看记录
- `PUT /api/records/{id}` - 更新观看记录
- `DELETE /api/records/{id}` - 删除观看记录
- `GET /api/records/stats` - 获取统计数据
  - 返回: 各状态数量、评分分布、观看趋势等
- `GET /api/records/export` - 导出记录(CSV/JSON格式)

**数据同步API**:
- `POST /api/sync` - 手动触发数据同步
  - 参数: full_sync(是否全量同步), sync_types(同步哪些数据类型)
- `GET /api/sync/status` - 获取同步状态和进度
- `GET /api/sync/history` - 获取同步历史记录
- `GET /api/sync/latest-version` - 获取最新可用数据版本

#### 4. 前端页面设计

**首页 (Home)**:
- 展示最新更新的内容
- 快速搜索入口
- 统计概览(总条目数、用户记录数等)

**列表页 (AnimeList/GameList/etc)**:
- 网格/列表视图切换
- 多维度筛选(年份、类型、标签、状态等)
- 排序功能(评分、日期、热度等)
- 分页加载

**搜索页 (Search)**:
- 全文搜索
- 高级搜索选项
- 搜索结果分类展示

**我的记录 (MyRecords)**:
- 按状态分类展示(想看/在看/看过等)
- 进度管理
- 评分和评论
- 数据统计图表

#### 5. 搜索和筛选功能

**搜索功能**:
- 支持标题(中日英)模糊搜索
- 支持标签搜索
- 支持简介关键词搜索
- Elasticsearch集成(可选，数据量大时)

**筛选功能**:
- 年份范围
- 类型分类
- 标签多选
- 评分区间
- 放送状态
- 集数范围

---

### 四、开发阶段规划

#### 第一阶段：基础架构搭建 (预计1-2周) ✅ 已完成
- [x] 初始化项目结构
- [x] 配置后端FastAPI框架
- [x] 配置前端Vue3项目
- [x] 设计并实现数据库模型(SQLAlchemy models)
- [x] 实现基础的CRUD API
- [x] 配置CORS和跨域支持
- [x] 配置数据库迁移工具(Alembic)

#### 第二阶段：数据同步模块 (预计1-2周) ✅ 已完成
- [x] 实现GitHub Archive数据下载功能
  - 解析latest.json获取最新版本
  - 下载subject.jsonlines等数据文件
- [x] 实现JSON Lines文件解析器
  - 逐行读取和处理大规模数据
  - 批量插入优化
- [x] 集成wiki-parser-py(bgm-tv-wiki)解析infobox
  - 解析Wiki语法为结构化数据
  - 提取关键信息(话数、放送时间、制作公司等)
- [x] 实现数据导入数据库逻辑
  - Subject主表导入 (639,483条)
  - Episode/Person/Character关联数据导入 (~1.9M条)
  - 关系表数据导入 (~3.6M条)
- [x] 实现增量更新机制
  - 记录最后同步时间和版本号
  - 对比新旧数据差异
- [x] 实现定时同步任务(APScheduler)
  - 每周三凌晨5点自动同步
  - 同步失败重试机制
- [x] 编写数据同步测试（Phase 5 已补充 Pytest 42 用例）

#### 第三阶段：核心API开发 ✅ 已完成
- [x] 实现条目查询API (Subjects)
  - 列表查询(分页、排序、9种筛选) — 支持 type/search/tag/date/score/nsfw/series/sort/order
  - 详情查询(包含关联数据) — episodes/characters(CV)/persons(STAFF)/relations
  - 搜索功能 — LIKE 匹配 name/name_cn/name_en，按匹配质量排序
- [x] 实现剧集/人物/角色API
  - Episodes API — 按 subject_id 查询 + 单集详情
  - Persons API — 列表(搜索+筛选) + 详情(参与作品+CV角色)
  - Characters API — 列表(搜索+筛选) + 详情(出场作品+CV)
- [x] 实现关联数据API
  - GET /api/subjects/{id}/relations — 条目关联(续作/前传等)
  - GET /api/subjects/{id}/characters — 条目角色(含CV)
  - GET /api/subjects/{id}/persons — 条目STAFF
- [x] 实现用户记录管理API
  - CRUD操作 — 创建/更新/删除观看记录
  - 统计分析 — GET /api/records/stats (状态分布/评分分布/类型分布)
  - 在看追番 — GET /api/records/watching (含剧集列表 + 逐集状态)
  - Bangumi 导入 — POST /api/records/import (支持 bgm collections JSON 格式)
  - 按条目过滤 — GET /api/records?subject_id= (新增 subject_id 查询参数)
- [x] 实现数据同步管理API (Phase 2 完成)
- [x] API文档完善 — Swagger UI 自动生成，28个端点全部可交互
- [x] API性能优化 — 4个新复合索引 + selectinload 预加载避免 N+1

#### 第四阶段：前端页面开发 ✅ 已完成
- [x] 实现基础布局和导航
  - 响应式布局 — 移动端汉堡菜单 + 侧边栏折叠
  - 路由配置 — 5个懒加载路由
  - 状态管理 — 3个 Pinia Store (subjects/records/search)
- [x] 实现条目列表页
  - 网格/列表视图切换 — Element Plus 按钮组切换
  - 多维度筛选面板 — SubjectFilters 组件(类型/日期/评分/NSFW/系列)
  - 排序和分页 — 5种排序 + el-pagination
- [x] 实现条目详情页
  - 基本信息展示 — 名称/评分/排名/日期/标签
  - infobox解析后信息展示 — InfoboxDisplay 组件(el-descriptions)
  - 剧集列表 — EpisodeList 组件(按disc分组)
  - 角色和STAFF列表 — CharacterGrid + StaffList 组件
  - 关联条目推荐 — 可点击跳转的关联卡片
- [x] 实现搜索功能
  - 多 scope 搜索 — 条目/人物/角色/全部，Tab 切换
  - 搜索结果高亮 — `<mark>` 标签高亮匹配词
- [x] 实现用户记录管理界面
  - 状态 Tab 切换 — 全部/想看/在看/看过/搁置/抛弃
  - 编辑弹窗 — 状态/进度/评分(RatingInput)/评论
  - CRUD操作 — 新建/编辑/删除，带确认和成功提示
  - 统计卡片 — 总记录/状态分布/评分分布/类型分布
- [x] 实现首页仪表盘
  - 快速搜索入口
  - 数据总量展示 — 条目/人物/角色总数 + 最后同步时间
  - 个人统计概览 — 观看记录状态分布
  - 高分推荐 + 最新更新 — SubjectCard 网格展示
  - **在看在追点格子** — 首页展示正在观看的条目剧集点格子，点击即时标记已看/未看，自动更新 ep_status 和 progress
- [x] 实现条目卡片快速记录操作
  - 悬停浮现「想看」「看过」快捷按钮（Grid 模式），新增「+」完整记录按钮
  - 列表模式常驻「想」「✓」按钮，新增「+记录」文字按钮
  - 点击「+」打开完整记录编辑弹窗（状态/进度/评分/评论），默认状态为「在看」
- [x] 实现 Bangumi 在线记录导入
  - 支持 Bangumi 官方导出的 collections JSON 格式
  - 自动映射状态类型（bgm: 1→1, 2→3, 3→2, 4→4, 5→5）
  - 自动去重：同一用户+条目已有记录则更新，否则新增
  - 返回导入统计结果（created / updated / skipped / errors）
- [x] 实现进度选择限制
  - 详情页进度输入根据条目剧集数自动设置 max
  - 记录管理页编辑弹窗根据 episode_count 限制进度最大值，显示「共 N 集/章」提示
  - 后端所有记录查询响应新增 episode_count 字段，批量查询避免 N+1
- [x] 实现响应式设计 — Element Plus 栅格 xs/sm/md/lg

#### 第五阶段：优化和完善 ✅ 已完成
- [x] 性能优化
  - 数据库索引优化 — 初始迁移已包含全部必要索引
  - 查询优化(N+1问题) — SubjectDetail 使用 selectinload + 批量查询
  - Redis缓存 — 跳过(本地SQLite桌面应用不适合)
  - 前端资源懒加载 — 路由级 lazy import + vite manualChunks (主包 49KB)
- [x] 错误处理和日志完善
  - 统一异常处理 — FastAPI 全局异常处理器(HTTP/422/SQLAlchemy/兜底)
  - 详细日志记录 — RotatingFileHandler(10MB×5) + 控制台输出
  - 请求日志中间件 — method/path/status/duration
- [x] 单元测试和集成测试
  - 后端API测试 — Pytest 42个测试用例全部通过
  - 前端组件测试 — 跳过(Vitest 可选补充)
  - 端到端测试 — 跳过(Cypress 可选补充)
- [x] 用户体验优化
  - 加载动画 — el-skeleton 骨架屏
  - 错误提示优化 — ElMessage 统一提示(成功/警告/错误)
  - 键盘快捷键 — `/` 键全局跳转搜索
- [x] 文档完善
  - API文档 — Swagger/OpenAPI 自动生成
  - 部署文档 — 见下方快速开始
  - README更新 — 阶段完成状态标记

#### 第六阶段：部署和发布 (预计3-5天)
- [ ] Docker容器化配置
  - 后端Dockerfile
  - 前端Dockerfile
  - docker-compose.yml
- [ ] 编写部署文档
- [ ] 生产环境配置
  - 环境变量管理
  - 数据库备份策略
  - 日志轮转
- [ ] 数据备份方案
  - 自动备份脚本
  - 备份恢复测试
- [ ] 正式发布
  - GitHub Release
  - 版本标签

---

### 五、关键技术实现细节

#### 1. GitHub Archive数据获取策略

```python
# 伪代码示例
class ArchiveFetcher:
    def get_latest_version(self):
        # 1. 请求 https://github.com/bangumi/Archive/raw/master/aux/latest.json
        # 2. 解析JSON获取最新版本号和文件URL
        # 3. 返回版本信息
    
    def download_archive(self, version):
        # 1. 从latest.json获取下载URL
        # 2. 下载tar.gz或zip文件
        # 3. 解压到临时目录
        # 4. 返回文件路径
    
    def parse_jsonlines(self, file_path, batch_size=1000):
        # 1. 逐行读取.jsonlines文件
        # 2. 每行解析为JSON对象
        # 3. 批量处理(提高性能)
        # 4. 生成器模式，节省内存
    
    def incremental_sync(self):
        # 1. 检查本地最后同步版本号
        # 2. 对比最新版本号
        # 3. 如果有更新，下载新数据
        # 4. 增量更新数据库记录
```

#### 2. Wiki Infobox解析

```python
# 使用wiki-parser-py解析infobox
from wiki_parser import parse_wiki_text

def parse_infobox(infobox_raw: str) -> dict:
    """
    解析Wiki语法的infobox字段
    
    输入:
    {{Infobox animedetail
    |中文名 = 星际牛仔
    |别名 = Cowboy Bebop
    |话数 = 26
    }}
    
    输出:
    {
        "中文名": "星际牛仔",
        "别名": "Cowboy Bebop",
        "话数": "26"
    }
    """
    parsed = parse_wiki_text(infobox_raw)
    # 提取关键字段
    return extract_key_fields(parsed)
```

#### 3. JSON Lines大数据处理

```python
import json
from typing import Generator

def read_jsonlines(file_path: str) -> Generator[dict, None, None]:
    """
    逐行读取JSON Lines文件，节省内存
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def batch_insert(session, records, batch_size=500):
    """
    批量插入数据库，提高性能
    """
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        session.bulk_insert_mappings(Subject, batch)
        session.commit()
```

#### 4. 数据库优化

- **索引策略**:
  - subjects表: bangumi_id (UNIQUE), type, name_cn, date, score, updated_at
  - episodes表: subject_id, airdate, sort
  - user_records表: user_id, subject_id, status
  - 联合索引: (type, score), (type, date)等常用查询组合

- **查询优化**:
  - 使用连接池管理数据库连接
  - 避免N+1查询问题(使用joinedload/selectinload)
  - 分页查询使用游标分页而非OFFSET
  - 定期VACUUM数据库(SQLite)

- **数据库迁移**:
  - 使用Alembic管理数据库schema变更
  - 编写迁移脚本确保数据安全

#### 5. 缓存策略

- **后端缓存** (可选):
  - Redis缓存热门条目查询结果
  - 缓存标签列表、统计数据等不常变化的数据
  - 设置合理的TTL(过期时间)

- **前端缓存**:
  - 浏览器localStorage缓存用户偏好
  - Service Worker缓存静态资源(PWA)
  - API响应使用ETag和If-None-Match

#### 6. 错误处理

- **后端**:
  - 统一的异常处理中间件
  - HTTPException返回标准错误格式
  - 详细的日志记录(logging模块)
  - 网络请求自动重试(httpx + tenacity)

- **前端**:
  - Axios拦截器统一处理错误
  - 友好的错误提示(Element Plus Message)
  - 网络异常重试机制
  - 降级方案(离线数据)

#### 7. 数据类型映射

```python
# Bangumi type字段映射
TYPE_MAPPING = {
    1: "comic",      # 漫画
    2: "anime",      # 动画
    3: "music",      # 音乐
    4: "game",       # 游戏
    6: "real",       # 三次元
}

# Platform映射(需参考bangumi/common仓库)
PLATFORM_MAPPING = {
    1: "TV",
    2: "剧场版",
    3: "OVA",
    4: "Web",
    # ... 更多映射
}

# Episode type映射
EPISODE_TYPE_MAPPING = {
    0: "正篇",
    1: "特别篇",
    2: "OP",
    3: "ED",
    4: "Trailer",
    5: "MAD",
    6: "其他",
}
```

---

### 六、安全性考虑

1. **输入验证**: 使用Pydantic进行严格的输入验证
2. **SQL注入防护**: 使用ORM避免原生SQL
3. **XSS防护**: 前端对用户输入进行转义
4. **CORS配置**: 限制允许的域名
5. **速率限制**: 防止API滥用(可选)
6. **数据备份**: 定期备份数据库

---

### 七、扩展性设计

1. **多用户支持**: 预留user_id字段，未来可添加用户系统
2. **插件化架构**: 数据源可扩展(不仅限于GitHub)
3. **API版本控制**: 支持多版本API共存
4. **微服务拆分**: 前后端分离，便于独立扩展
5. **国际化**: 预留i18n支持

---

### 八、开发规范和约定

#### 代码规范
- Python遵循PEP 8规范
- JavaScript遵循Airbnb风格指南
- 提交信息遵循Conventional Commits规范
- 所有代码必须通过lint检查

#### Git工作流
- 采用Git Flow分支策略
- main: 生产环境分支
- develop: 开发分支
- feature/*: 功能分支
- hotfix/*: 热修复分支

#### 文档要求
- 所有API必须有文档说明
- 复杂逻辑必须添加注释
- 保持README及时更新

---

### 九、测试策略

1. **单元测试**: 测试各个函数和方法的正确性
2. **集成测试**: 测试API接口的完整流程
3. **端到端测试**: 测试前端页面的交互(可选)
4. **性能测试**: 测试高并发下的表现(可选)

测试覆盖率目标: 80%以上

---

### 十、后续优化方向

1. **移动端适配**: 开发移动端App或PWA
2. **社交功能**: 分享、好友系统等
3. **推荐算法**: 基于用户喜好的推荐
4. **数据统计**: 更丰富的可视化图表
5. **离线支持**: PWA离线浏览功能
6. **多数据源**: 整合其他ACGN数据库
7. **AI辅助**: 智能标签、自动分类等

---

### 十一、数据来源说明

#### Bangumi Archive项目

本项目使用的数据来源于 [Bangumi Archive](https://github.com/bangumi/Archive)，这是Bangumi官方提供的数据导出服务。

**数据特点**:
- **更新频率**: 每周三凌晨五点(GMT+8)更新
- **数据格式**: JSON Lines (.jsonlines)，每行一个独立的JSON对象
- **数据内容**: 包含条目的原始Wiki内容和结构化字段
- **获取方式**: 通过GitHub Releases下载

**主要数据文件**:
1. **subject.jsonlines** (核心数据)
   - 包含所有ACGN条目信息
   - 字段: id, type, name, name_cn, infobox, platform, summary, date, tags, score, rank等
   - 文件大小: 约几百MB到几GB

2. **episode.jsonlines** (剧集数据)
   - 包含所有章节/剧集信息
   - 字段: id, subject_id, name, name_cn, airdate, sort, type等

3. **person.jsonlines** (人物数据)
   - 包含STAFF和声优信息
   - 字段: id, name, type, career, infobox, summary等

4. **character.jsonlines** (角色数据)
   - 包含动漫角色信息
   - 字段: id, name, role, infobox, summary等

5. **关联数据文件**:
   - subject_relations.jsonlines: 条目间关联
   - subject_characters.jsonlines: 条目-角色关联
   - subject_persons.jsonlines: 条目-人物关联
   - person_characters.jsonlines: 人物-角色(CV)关联
   - person_relations.jsonlines: 人物/角色间关联

**数据版本管理**:
- 通过 `aux/latest.json` 文件获取最新版本信息
- 每个版本有唯一的版本号和时间戳
- 支持增量更新，无需每次都全量下载

**Wiki语法解析**:
- infobox字段存储的是原始Wiki字符串
- 需要使用专门的解析器转换为结构化数据
- 参考项目:
  - [wiki-parser-go](https://github.com/bangumi/wiki-parser-go)
  - [wiki-parser](https://github.com/bangumi/wiki-parser)
  - [wiki-parser-py](https://github.com/bangumi/wiki-parser-py)
  - [wiki-syntax-spec](https://github.com/bangumi/wiki-syntax-spec)

**常量定义**:
- relation_type, platform, position等常量的映射关系
- 参考 [bangumi/common](https://github.com/bangumi/common) 仓库的YAML文件

**使用注意事项**:
1. 数据量较大，首次同步可能需要较长时间
2. 建议实现增量更新机制，减少网络流量
3. 注意处理HTML转义字符(infobox中可能包含)
4. 部分字段可能为空或格式不规范，需要容错处理
5. NSFW内容需要根据需求决定是否导入

**数据许可**:
- 请遵守Bangumi的数据使用协议
- 仅用于个人学习和研究目的
- 不要用于商业用途
- 尊重原作者的知识产权

---

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- Git

### 安装步骤
(待补充具体安装命令)

### 运行项目
(待补充启动命令)

---

## 贡献指南

欢迎提交Issue和Pull Request！

---

## 许可证

MIT License
