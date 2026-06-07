# Codex 提示词

## Prompt 001：初始化仓库

请先阅读：

- AGENTS.md
- docs/产品说明.md
- docs/系统架构.md
- docs/开发路线图.md
- docs/任务清单.md

只实现 Task 001。

要求：

- 创建最小 Python 包结构。
- 添加 pyproject.toml。
- 添加 index_platform 包。
- 添加 tests 目录。
- 添加 pytest 配置。
- 添加最小 CLI 入口。
- 暂时不要实现真实金融数据、回测或策略逻辑。

验收标准：

- pytest 通过。
- python -m index_platform.cli.main --help 可以运行。
- 总结修改了哪些文件。

不要实现 Task 002 或更后面的任务。

## Prompt 002：添加指数注册表

请先阅读 AGENTS.md 和 docs/任务清单.md。

只实现 Task 002。

要求：

- 添加 configs/indices.yaml。
- 添加 index_platform/universe/registry.py。
- 添加指数注册表读取和过滤测试。

初始指数样例包括：

A 股：

- 000300.SH 沪深300
- 000905.SH 中证500
- 000852.SH 中证1000
- 000016.SH 上证50

港股：

- HSI.HK 恒生指数
- HSCEI.HK 恒生中国企业指数
- HSTECH.HK 恒生科技指数

美股：

- SPX.US S&P 500
- IXIC.US Nasdaq Composite
- NDX.US Nasdaq 100
- DJI.US Dow Jones Industrial Average

验收标准：

- 可以读取全部指数。
- 可以按 market 过滤。
- pytest 通过。

不要实现数据下载。

## Prompt 003：添加 CSV 数据适配器

请先阅读 AGENTS.md 和 docs/任务清单.md。

只实现 Task 003。

要求：

- 添加价格数据 schema。
- 添加 CSV adapter。
- 添加必需字段校验。
- 添加 toy CSV 测试数据和测试。

暂时不要加入 AKShare、Tushare、yfinance。

验收标准：

- 可以读取 CSV。
- 可以校验必需字段。
- 可以标准化 date 字段。
- pytest 通过。

## Prompt 004：添加 Parquet 存储

请先阅读 AGENTS.md 和 docs/任务清单.md。

只实现 Task 004。

要求：

- 添加本地 Parquet 存储。
- 实现 save_price_data。
- 实现 load_price_data。
- 支持 symbol、start date、end date 过滤。
- 添加测试。

验收标准：

- 保存和读取正常。
- 过滤正常。
- pytest 通过。

## Prompt 005：实现买入持有回测

请先阅读 AGENTS.md 和 docs/任务清单.md。

只实现 Task 005。

要求：

- 添加基础策略接口。
- 添加 buy-and-hold 策略。
- 添加简单日频回测引擎。
- 使用 close price。
- 生成 NAV 序列。
- 添加 toy price series 测试。

规则：

- 不做杠杆。
- 不做卖空。
- 不做分钟级数据。
- 不做实盘交易。
- 明确记录执行规则。

验收标准：

- 简单价格序列下 NAV 正确。
- pytest 通过。