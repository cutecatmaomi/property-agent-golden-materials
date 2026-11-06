# Golden Questions · 确定性守卫补件

本补件用于把已交付的 `GOLDEN_QUESTIONS_100` 原系统规则接入 Enact 的前置流程。`response_policy.py` 从交接包逐字复制，完整包含 31 条红线词、1 条红线正则、14 条人工服务词、NFKC 和固定话术。

| 文件 | 用法 |
|---|---|
| `response_policy.py` | 原系统规则，直接导入 `classify_message` 和 `fixed_reply` |
| `enact_guard.py` | Python 接入函数和 stdin/stdout JSON 入口 |
| `Enact技能前置规则.md` | 合入现有技能的接入约定，附完整词表、正则和固定话术 |
| `guard_rules.json` | 给接入方逐项比对规则 |
| `FIXED_SERVICE_REPLY.txt` | 原话术 UTF-8 字节 |
| `guard_cases.json`、`verify_guard.py` | 测试输入、期望路由和可执行的本地校验 |
| `verification.json` | 本次测试结果和原系统对齐结果 |

## 接入执行顺序

在服务端认证会话并校验本轮输入后，调用守卫。然后按 `handled` 选择分支。命中时由界面直接渲染 `reply.text`，保留 `reply.data.reason_code`，结束本轮处理。未命中时继续既有 Golden Questions 知识和业务流程。守卫运行失败时，由宿主记录错误并暂停该轮。

若 Enact 技能是在模型调用之后才执行，前置守卫应接在请求编排器或 daemon 的入站处理处。技能段作为执行约定，程序负责匹配。

Python 中可直接导入。

```python
from enact_guard import guard_message

result = guard_message(user_message, estate_id=authenticated_estate_id)
```

也可以用 stdin 传入单个 JSON 对象。该 `estate_id` 取自认证会话，以下是合成示例。

```bash
printf '%s\n' '{"message":"请帮我转人工客服。","estate_id":"E001"}' | python3 enact_guard.py
```

命中时 stdout 为 `{"handled":true,"reply":{...}}`，其中 reply 与原 Agent 的固定分支结构一致。未命中时为 `{"handled":false,"reply":null}`。工具只需 Python 标准库。

运行 `python3 -B verify_guard.py` 可核验词表、原话术、两类优先级、Unicode 归一化、正则、游乐设施例外和普通报修继续流转。平台接入后，用同一组 JSON 检查命中分支的模型调用数与业务写入数均为零。
