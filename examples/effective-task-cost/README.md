# 总费用不高，为什么每个有效结果仍然贵？用 CSV 离线复算

Offline, per-currency cost per qualified task using Python's standard library.

同一批任务的总费用看起来不高，失败、返工和零合格结果仍可能把单位成本推高。这个可复查的 CSV 示例帮助开发者和采购团队把费用与业务合格结果放到同一张表里，按币种算出总任务数、合格数、总费用和每个合格结果成本。工具不判断结果质量，合格标准必须由使用者事先定义。

## 环境与费用

- Python 3.10 或以上；仅标准库，无第三方安装依赖。
- 不需要 API 密钥或环境变量，不联网、不登录账户、不产生 API 调用费。
- `sample.csv` 为完全虚构的数据，不是客户账单、供应商报价或 CodingRouter 价格。
- 不验证模型身份、真实价格、性能、线上 API 兼容性或费用归属是否准确。

## 运行

在本目录执行：

```bash
python calculate.py sample.csv
python -m unittest discover -s . -p "test_*.py" -v
```

Windows 若 `python` 不可用，可替换成已安装 Python 解释器的完整路径。

## 输入契约

UTF-8 CSV（支持 UTF-8 BOM），第一行恰好包含 `task_id,currency,total_cost,qualified` 四个列名，顺序可调整；其他列或重复列名拒绝。每行代表一个已结束任务，至少一条任务。字段两端空白会去掉，CSV 空白行忽略。

| 字段 | 要求 |
| --- | --- |
| task_id | 非空，整个文件内唯一，跨币种也不能重复 |
| currency | 三个大写 ASCII 字母，分组标识；不校验 ISO 币种目录，不自动换汇 |
| total_cost | 非负普通十进制定点数，1—12 位整数，可选 1—6 位小数；不接受科学计数法、符号、下划线、NaN 或 Infinity |
| qualified | 仅接受小写 `true` 或 `false` |

`total_cost` 应包含该任务所有实际归属的已计费重试或追加轮次；失败任务的费用也计入分子。工具不会推断哪些失败请求应当计费，须先依据真实账单规则整理输入。不得把不同价格单位或不同费用口径混在同一列。

空文件、仅表头、缺字段、空值、无效数值、负值、无效 qualified、重复 task_id 和损坏 CSV 都会失败，返回退出码 2、错误写 stderr、stdout 不输出部分汇总。错误只报告位置/字段规则，不回显原始值或文件路径。成功返回退出码 0。

## 样例与预期结果

样例中 CNY 三个任务费用分别为 0.10、0.20、0.15，其中第二个不合格；另有 USD 一个不合格任务，费用 0.03。预期输出：

```json
[
  {
    "currency": "CNY",
    "task_count": 3,
    "qualified_count": 2,
    "total_cost": "0.450000",
    "cost_per_qualified_result": "0.225000"
  },
  {
    "currency": "USD",
    "task_count": 1,
    "qualified_count": 0,
    "total_cost": "0.030000",
    "cost_per_qualified_result": null
  }
]
```

金额输出为字符串，避免 JSON 浮点精度损失；总额用整数微单位精确累加，每个合格结果成本用 Decimal 计算，保留六位小数并四舍五入（ROUND_HALF_UP）。合格数为零时 `null` 表示“不可计算”，不表示零成本。小数位显示规则不是任何真实货币的结算规则。

## 验证与限制

2026-10-21 发布核验对应 [PR #2](https://github.com/CodingRouter-zane/codingrouter-cookbook/pull/2) 的固定 head `63bb0fde`：Windows / Python 3.12.14 的原交付验证及 Linux / Python 3.12.14 的发布前辅助复核均为 22 项 unittest 通过，样例 CLI 与 `py_compile` 退出码 0。两次均未使用 API 密钥或联网调用；进入 main 的 Python 与测试文件和已复核 head 一致。

测试覆盖单/多币种、失败任务费用、零合格数、固定小数精度与舍入、输入边界、坏行不输出部分结果，以及真实 CLI 子进程退出状态。Python 3.10+ 是运行前提，但本次没有逐版本实测；验证范围仅为本地离线 CSV 逻辑，不等于真实账单审计或线上 API 实测。

输入全量验证后才输出结果；任务 ID 去重使用内存，不面向无限规模账单。仅支持文档规定的金额精度。全仓库尚未选定许可证，本示例不替用户选择全仓库许可证，也不复制第三方源代码。
