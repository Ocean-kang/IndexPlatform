# IndexPlatform

IndexPlatform 是一个本地优先的指数投资研究与回测项目。当前阶段聚焦于指数基础数据、CSV 导入、本地 Parquet 存储、策略回测、指标计算、结果保存、命令行工具和轻量级 Streamlit Dashboard。

本项目不是实盘交易系统，不包含券商接口、下单、账户管理或投资建议功能。

## 当前已实现功能

- 从 `configs/indices.yaml` 读取指数注册表，并支持按市场过滤。
- 导入本地日频价格 CSV，进行字段规范化和基础数据质量检查。
- 使用 Parquet 保存本地价格数据，并提供 DuckDB 查询辅助模块。
- 支持买入持有、均线择时、动量轮动三类基础策略。
- 支持单资产和多资产的日频多头回测，包含基础交易成本处理。
- 支持通过 YAML 配置运行回测，并将结果保存到 `outputs/backtests/`。
- 保存回测净值、持仓、交易记录和指标，并可生成 Markdown 风格报告。
- 计算总收益、年化收益、波动率、最大回撤、Sharpe、Calmar 等基础绩效指标。
- 提供参数扫描、滚动样本评估等研究辅助模块。
- 提供本地运行状态和日志记录，用于查看回测运行结果。
- 提供 Streamlit Dashboard 页面：数据状态、指数列表、策略实验、回测结果、运行监控。
- 提供基础预测模块和预测策略接口，目前只包含轻量 baseline 能力。
- 提供 ETF 映射表读取能力，用于研究查询。

## 当前仅为基础骨架的部分

- `index_platform/data/adapters/` 中包含 AKShare、港股、yfinance 相关适配器，但第三方数据源可用性取决于外部库和网络环境。
- `index_platform/prediction/` 目前不是完整机器学习训练系统，不包含模型持久化、自动调参或生产级预测流程。
- Dashboard 是本地研究界面，复用核心模块，但不是完整多用户 Web 系统。
- 运行监控仅基于本地状态文件和日志文件，不是分布式任务调度系统。

## 未实现功能

- 实盘交易、券商 API、订单管理、账户管理。
- 分钟级或 Tick 级交易。
- 融资融券、杠杆、做空、期货、期权等复杂交易机制。
- 生产级机器学习平台、深度学习训练和模型服务。
- 云端部署、多用户权限、任务队列和自动化调度。
- 对第三方行情源可用性的保证。

## 仓库目录结构

```text
index_platform/
  analysis/      指数比较辅助模块
  backtest/      回测引擎、交易成本和回测编排
  calendar/      简单交易日历工具
  cli/           Typer 命令行入口
  config/        回测 YAML 配置读取
  dashboard/     Streamlit 本地可视化界面
  data/          数据 schema、CSV 导入、校验、外部数据适配器
  fx/            本地汇率数据和换算辅助
  metrics/       绩效指标计算
  monitor/       本地运行状态和日志
  prediction/    基础预测接口和 baseline
  report/        回测报告生成
  research/      参数扫描和滚动样本评估
  storage/       Parquet、DuckDB 和回测结果存储
  strategy/      策略实现
  universe/      指数注册表和 ETF 映射

configs/
  indices.yaml
  etf_mapping.yaml
  strategies/

examples/
  configs/
  data/

docs/
  产品说明.md
  系统架构.md
  开发路线图.md
  任务清单.md
  CODEX提示词.md

tests/
  analysis/
  backtest/
  calendar/
  cli/
  config/
  dashboard/
  data/
  fx/
  metrics/
  monitor/
  prediction/
  report/
  research/
  storage/
  strategy/
  universe/
```

## 核心模块说明

- `index_platform.universe`：读取指数注册表和 ETF 映射配置。
- `index_platform.data`：读取本地日频价格 CSV，完成字段规范化和基础校验。
- `index_platform.storage`：保存和读取 Parquet 价格数据、查询本地数据、保存回测结果。
- `index_platform.strategy`：实现 `buy_hold`、`moving_average`、`momentum` 等策略。
- `index_platform.backtest`：执行日频回测，并由 runner 统一承接 CLI 和 Dashboard 调用。
- `index_platform.metrics`：计算回测绩效指标。
- `index_platform.research`：提供参数扫描和 walk-forward 辅助。
- `index_platform.report`：读取已保存回测结果并生成报告文本。
- `index_platform.monitor`：记录和读取本地回测运行状态。
- `index_platform.dashboard`：基于 Streamlit 的本地研究界面。

## Windows + Miniconda 安装

建议使用 Python 3.10。以下命令以 Windows PowerShell 和 Miniconda 为例：

```powershell
conda create -n indexplatform python=3.10 -y
conda activate indexplatform
python -m pip install -e ".[dev]"
```

如需使用可选第三方行情适配器，可按需安装：

```powershell
python -m pip install akshare yfinance
```

安装后可以使用模块入口：

```powershell
python -m index_platform.cli.main --help
```

`pyproject.toml` 同时定义了 `idx` 命令入口。 editable 安装完成后，也可以尝试：

```powershell
idx --help
```

## CLI 使用方式

查看帮助：

```powershell
python -m index_platform.cli.main --help
```

列出注册指数：

```powershell
python -m index_platform.cli.main list-indices
python -m index_platform.cli.main list-indices --market CN
```

查看运行状态：

```powershell
python -m index_platform.cli.main monitor status
```

查看已保存回测报告：

```powershell
python -m index_platform.cli.main report show --run-id <run_id> --runs-dir outputs/backtests
```

## 自动下载指数历史数据

`data import` 用于导入已经准备好的本地 CSV 文件；`data fetch` 用于从在线数据源提取注册表中的指数日线数据。两者最终都会写入本地 `data/parquet/prices.parquet`，供 CLI、回测引擎和 Dashboard 复用。

在线提取当前按市场选择数据源：

- CN 市场优先使用 AKShare，平台 symbol 会映射为 AKShare symbol，例如 `000300.SH -> sh000300`。
- US 市场使用 yfinance，例如 `SPX.US -> ^GSPC`。
- HK 市场使用港股 yfinance 适配器，例如 `HSI.HK -> ^HSI`。

如果还没有安装在线数据源依赖，Windows + Miniconda 环境中可运行：

```powershell
conda activate indexplatform
python -m pip install akshare yfinance
```

下载单个指数：

```powershell
python -m index_platform.cli.main data fetch --symbol 000300.SH --start-date 2010-01-01 --end-date 2026-06-07 --data-dir data/parquet
```

下载某个市场的全部注册指数：

```powershell
python -m index_platform.cli.main data fetch --market CN --start-date 2010-01-01 --end-date 2026-06-07 --data-dir data/parquet
```

下载注册表里的全部指数：

```powershell
python -m index_platform.cli.main data fetch --all --start-date 2010-01-01 --end-date 2026-06-07 --data-dir data/parquet
```

`data fetch` 会先下载本次目标指数，再和已有 `prices.parquet` 合并，按 `symbol + date` 去重，并让新下载的数据覆盖旧数据。批量下载时，单个指数失败不会中断其它指数保存；命令最后会输出成功数量、失败数量和失败列表。

## 示例数据导入

示例数据位于：

```text
examples/data/sample_index_prices.csv
```

CSV 字段包括：

```text
date,symbol,open,high,low,close,volume,amount,currency,source
```

导入示例数据：

```powershell
python -m index_platform.cli.main data import examples/data/sample_index_prices.csv --data-dir data/parquet
```

查看本地数据状态：

```powershell
python -m index_platform.cli.main data status --data-dir data/parquet
```

当前 Parquet 存储实现会写入 `data/parquet/prices.parquet`。重复导入会替换该文件，便于保持示例流程可复现。

## 示例回测运行

使用 YAML 配置运行买入持有示例：

```powershell
python -m index_platform.cli.main backtest run --config examples/configs/buy_hold_demo.yaml --data-dir data/parquet --output-dir outputs/backtests
```

仓库中还包含两个示例配置：

```powershell
python -m index_platform.cli.main backtest run --config examples/configs/moving_average_demo.yaml --data-dir data/parquet --output-dir outputs/backtests
python -m index_platform.cli.main backtest run --config examples/configs/momentum_demo.yaml --data-dir data/parquet --output-dir outputs/backtests
```

命令会输出 `Run ID`，并在 `outputs/backtests/<run_id>/` 下保存：

```text
config.yaml
nav.parquet
positions.parquet
orders.parquet
metrics.json
```

也可以直接对单个指数运行基础买入持有回测：

```powershell
python -m index_platform.cli.main backtest run 000300.SH --data-dir data/parquet
```

## Dashboard 启动方式

安装依赖后，在仓库根目录运行：

```powershell
streamlit run index_platform/dashboard/app.py
```

Dashboard 当前包含以下页面：

- `Data Status`：查看本地价格数据状态。
- `Index View`：查看指数注册表。
- `Strategy Lab`：通过界面触发基础策略回测。
- `Backtest Result`：查看已保存回测结果和净值曲线。
- `Run Monitor`：查看本地运行状态。

Dashboard 复用 `index_platform` 下的核心模块，不单独实现一套业务逻辑。

## 测试

运行测试：

```powershell
pytest
```

测试依赖来自 `.[dev]`，主要覆盖数据导入、校验、存储、策略、回测、指标、CLI、Dashboard 页面辅助函数、报告、监控和研究辅助模块。第三方数据源适配器测试使用 mock 或小型 DataFrame，不依赖真实网络下载。

## 当前限制

- 示例数据是小型合成日频数据，只用于验证本地流程。
- 当前回测模型较简化，结果依赖输入数据质量和策略假设。
- Parquet 价格存储当前采用单文件覆盖写入，不是增量数据湖。
- 多市场支持以配置和基础数据结构为主，真实数据接入仍需按数据源逐步完善。
- `configs/indices.yaml` 中指数注册信息用于研究和展示，不代表可交易标的。
- 本项目不提供收益承诺，也不能替代专业投资研究和风险控制。

## 后续计划

后续开发应继续遵循“小步实现、可测试、可复现、CLI 可调用、Dashboard 可复用”的原则，优先方向包括：

- 完善指数注册表和多市场元数据。
- 增强本地数据校验、缺失值处理和数据质量报告。
- 扩展策略配置、交易成本和回测统计。
- 改进 Dashboard 的交互和结果展示。
- 完善运行监控、报告导出和研究工作流。
- 在保持可测试的前提下逐步接入真实数据源。
