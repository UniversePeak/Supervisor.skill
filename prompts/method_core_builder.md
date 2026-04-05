# method_core.md 生成模板（预蒸馏方法论层）

## 任务

生成 `method_core.md`，作为导师 Skill 的 Part 0（通用方法论）。  
用于素材不足或导师方法论缺失时，补齐执行框架。

---

## 输入

- `distill_strategy`: strict_distill / hybrid_distill / template_first
- `use_template_methodology`: true / false
- `material_sufficiency_score`: 0-100
- 用户素材中的方法论信号（如：如何拆任务、如何推进、如何复盘）

---

## 输出模板

```markdown
# Method Core

## 蒸馏策略
- 当前策略：{distill_strategy}
- 模板方法论：{use_template_methodology}
- 素材充分度：{material_sufficiency_score}

## 任务拆解框架
1. {decompose_step_1}
2. {decompose_step_2}
3. {decompose_step_3}

## 优先级规则
1. {priority_rule_1}
2. {priority_rule_2}
3. {priority_rule_3}

## 风险分级
- 高风险：{risk_high}
- 中风险：{risk_mid}
- 低风险：{risk_low}

## 兜底策略
- 主线失败时切换条件：{fallback_trigger}
- 备选路径：{fallback_path}

## 输出要求
每次回答必须给：
1. 本周三步
2. 每步验收标准
3. 风险与备选方案
```

---

## 约束

1. `strict_distill` 时，尽量不用模板句式，优先用户素材
2. `hybrid_distill` 时，模板与素材可融合，标注 `[source=merged]`
3. `template_first` 时，可先给模板默认值，后续通过 update 渐进替换
