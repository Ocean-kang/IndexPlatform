# AGENTS.md

## 项目名称

IndexPlatform

## 项目目标

IndexPlatform 是一个指数投资研究平台，用于：

- 收集和整理指数数据
- 展示 A 股、港股、美股指数信息
- 回测指数投资策略
- 比较策略和基准指数表现
- 可视化策略净值、回撤、持仓和交易记录
- 监控策略运行状态

第一阶段只做研究和回测，不做实盘交易。

## 核心原则

不要一次性开发完整平台。

所有功能必须小步实现，每一步都要：

1. 简单
2. 可测试
3. 可复现
4. 可通过 CLI 调用
5. 可被可视化界面复用

CLI 和 dashboard 不能各写一套业务逻辑。  
CLI 和 dashboard 都必须调用同一套核心模块。

## 开发优先级

开发顺序如下：

1. 项目基础结构
2. 指数注册表
3. 本地数据存储
4. CSV 数据导入
5. 数据校验
6. 基础回测引擎
7. 买入持有策略
8. 均线择时策略
9. 动量轮动策略
10. 绩效指标
11. CLI 命令
12. Streamlit 可视化界面
13. 策略运行状态监控
14. 多市场支持
15. 预测模块

## 技术栈

使用 Python。

优先使用：

- typer：CLI
- rich：命令行展示
- pandas：数据处理
- numpy：数值计算
- pyarrow：Parquet 文件
- duckdb：本地分析查询
- pydantic：配置和 schema 校验
- pytest：测试
- streamlit：第一版可视化界面

不要引入过重依赖，除非当前任务确实需要。

## 目标目录结构

```text
index_platform/
  cli/
  data/
  storage/
  universe/
  strategy/
  backtest/
  metrics/
  dashboard/
  monitor/

configs/
  indices.yaml
  strategies/

docs/
  产品说明.md
  系统架构.md
  开发路线图.md
  任务清单.md
  CODEX提示词.md

tests/
  data/
  strategy/
  backtest/
  metrics/