# Mongolian Coal Auction (蒙煤拍卖数据看板与实时采集套件)

本项目提供了蒙古煤炭在线竞拍数据（comex.mse.mn）全自动采集、智能清洗、SQLite 持久化与纯离线可视化交互大屏套件。

---

## 一、 目录结构与架构划分

项目根目录下严格保持精炼，仅保留 3 个核心主文件，其余所有支撑模块与数据产物均按职能归入二级目录：

```text
Mongolian Coal Auction/
├── README.md                           # [根目录] 项目说明与架构文档
├── run_daily_sync.py                   # [根目录] 每日全自动同步入口主脚本
├── mongolia_coal_auction.html          # [根目录] 纯离线可视化大屏看板 (双击直开)
│
├── modules/                            # [二级目录] 核心采集与数据管理模块
│   ├── db_manager.py                   # SQLite 数据库管理、幂等落库与多维导出引擎
│   ├── fetch_comex_auction.py          # comex.mse.mn 实时拍卖看板数据采集接口
│   └── fetch_notices.py                # comex.mse.mn 通告清单与 PDF 供货条款抓取解析
│
└── data/                               # [二级目录] 数据持久化存储与产物归档
    ├── mongolian_coal_auction.db       # SQLite 核心结构化数据库 (历史与最新数据底座)
    ├── auction_data.js                 # 前端直连数据源 (挂载 window.COAL_AUCTION_DATA)
    ├── daily_auction_merged.json       # 今日最新拍卖 Join 关联数据快照
    └── 蒙煤拍卖临时记录.xlsx            # 全量历史拍卖台账 (格式化 Excel，兼顾人工查阅)
```

---

## 二、 核心文件与二级目录说明

### 1. 根目录文件 (Root Files)
* **`run_daily_sync.py`**：**唯一日常执行入口**。全自动抓取今日实时看板与详细通告，完成数据 Join 关联，幂等写入 SQLite，并同步更新 `data/` 目录下的 JSON、Excel 及前端直连 JS 文件。
* **`mongolia_coal_auction.html`**：**纯离线交互看板**。采用现代响应式暗色卡片风设计，支持本地浏览器通过 `file://` 协议双击直接秒开（免 HTTP 服务、免 CORS 拦截、无刷新闪烁），内置分煤种价格走势、溢价率分析、供标总量统计及一键导出 Excel 报表功能。
* **`README.md`**：系统全景架构、模块清单与运行使用指引。

### 2. `modules/` (核心功能模块)
* **`db_manager.py`**：封装 SQLite 数据库连接、表结构维护（`coal_auctions` 具备多维防重唯一索引）、历史 Excel 批量迁移及前端数据逆向导出 API。采用单文件轻量模式，不产生冗余临时日志缓存。
* **`fetch_comex_auction.py`**：负责调度 comex.mse.mn 实时交易看板 API，获取当天的场次标的、成交价、起拍价与流拍状态。
* **`fetch_notices.py`**：负责抓取中文通告清单与解析官方公告 PDF，提取交割供货时间、供货地点及公路/铁路运输方式。

### 3. `data/` (数据存储与产物)
* **`mongolian_coal_auction.db`**：**系统唯一核心数据底座**。永久归档全量历史拍卖记录，支持高频增量幂等更新。
* **`auction_data.js`**：由 `db_manager.py` 自动生成的静态数据桥梁，供 HTML 看板零跨域直接读取。
* **`daily_auction_merged.json`**：保留今日当日拍卖细节与通告详情的结构化快照。
* **`蒙煤拍卖临时记录.xlsx`**：高保真 Excel 格式化台账，保留原汁原味的排版、公式与单元格样式，供向上汇报或线下人工查阅。

---

## 三、 环境准备与运行指引

### 1. 安装 Python 依赖环境
确保已安装 Python 3.8+，在项目根目录下安装所需依赖包：
```bash
pip install -r requirements.txt
```

### 2. 每日日常一键全自动同步（推荐）
在终端中执行根目录下的调度脚本：
```bash
python3 run_daily_sync.py
```
> **执行动作**：
> 1. 自动连接 comex.mse.mn 获取今日最新拍卖与通告并清洗关联；
> 2. 幂等更新至 `data/mongolian_coal_auction.db`；
> 3. 自动同步刷新 `data/auction_data.js`、`data/daily_auction_merged.json` 与 `data/蒙煤拍卖临时记录.xlsx`；
> 4. 在控制台打印今日格式化拍卖汇总清单。

### 2. 打开可视化看板
* **全新统一数据台账模块**：整合所有煤种至单一台账卡片，支持**全品类 / 煤种胶囊按钮**秒级无缝切换，提供卖方机构下拉、成交状态（已成交/流拍/待出价）下拉及关键字即时过滤；
* 支持一键筛选中挥发份焦煤、洗精主焦煤、半软焦煤等价格与溢价走势；
* 台账卡片自带**【导出当前筛选结果】**与顶部**【导出 Excel】**，支持导出当前视图为标准 Excel 报表；
* 点击 **【保存长图】** 按钮可一键生成高清看板报告长图。

### 3. 数据维护与统计查询
如需查看 SQLite 库内历史统计摘要或重新触发全量导出：
```bash
python3 modules/db_manager.py
```
