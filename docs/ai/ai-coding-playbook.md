# AI Coding Playbook

## Core Operating Model

Every iteration follows:

1. Context
2. Brief
3. Spec
4. Product Review
5. Plan
6. Engineering Review
7. Tasks
8. Implement one task
9. Tests / Evals / Manual Verification
10. QA Review
11. Security Review
12. Ship Report
13. Retrospective
14. Rule Update

## Good Task Format

A good task includes:

- Goal
- Context
- Constraints
- Acceptance criteria
- Non-goals
- Files likely involved
- Verification method
- Risk level
- Rollback plan

## Bad Prompts

Avoid:

- 帮我优化一下
- 重构这个模块
- 完善这个功能
- 看看有什么问题
- 顺便整理一下代码

## Good Prompts

Use:

- 修复 X 场景下 Y 错误
- 只允许修改 A/B 文件
- 不新增依赖
- 验收标准是 1/2/3
- 必须提供测试或手动验证
- 输出风险和回滚方案

## AI Failure Patterns

### Scope Creep

Trigger:
AI starts fixing unrelated issues.

Rule:
Stop and create follow-up tasks. Do not include unrelated fixes in the current task.

### Over-engineering

Trigger:
AI introduces framework, abstraction, or generic layer for a small problem.

Rule:
Prefer direct implementation unless repetition already exists.

### No Verification

Trigger:
AI says complete without tests, evals, or manual verification.

Rule:
Completion requires evidence.

### Legacy Risk

Trigger:
AI modifies legacy code without understanding existing behavior.

Rule:
Run legacy scout and characterization test first.

### Data Reality Check

Trigger:
AI writes a test script that uses hardcoded, speculative dummy data rather than inspecting the actual dataset.

Rule:
Always read and parse sample configuration files (e.g., `subset.csv` or database dumps) to select a valid entity before running verification queries. Do not guess mock inputs.

### Provider Parity Risk

Trigger:
AI assumes uniform output schemas across different third-party API wrappers (e.g., DashScope vs OpenAI).

Rule:
When switching or handling LLM APIs, verify the exact return object structure. Different providers may wrap structured JSON outputs inside Markdown blocks instead of returning dictionaries.