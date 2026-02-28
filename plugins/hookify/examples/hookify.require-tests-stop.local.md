---
name: require-tests-run
enabled: false
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: npm test|pytest|cargo test
---

**对话记录中未检测到测试!**

在结束之前, 请运行测试以验证修改是否正常工作.

测试命令示例:
- `npm test`
- `pytest`
- `cargo test`

**注意:** 如果对话记录中没有测试命令, 此规则会阻止结束.
仅在需要严格强制测试时启用此规则.
