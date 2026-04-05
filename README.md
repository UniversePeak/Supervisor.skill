<div align="center">

# 导师.skill

> *"你已经是这个领域的专家了"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

**天下硕博苦导师久矣，把导师蒸馏成 AI Skill，让抽象的交流变成你可执行的动作。**

<br>

一句话描述导师 + 一批原材料（批注/组会/聊天/邮件）<br>
生成一个可持续进化的导师 Skill：<br>
**Method Core + Academic Style + Persona + Graduation Playbook**

[功能特性](#功能特性) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [项目结构](#项目结构)

</div>

---

## 功能特性

### 1) 显式“务实模式”开关

创建时必须二选一：

- **学术理想型（academic_ideal）**：优先方法严谨、长期价值、完整性
- **毕业优先型（graduation_first，含合理裁缝）**：在导师红线内优先毕业可交付

> “合理裁缝”仅指：问题重述、实验组织、叙事优化、优先级取舍。  
> 不包含：伪造/篡改数据、抄袭、虚构引用、隐瞒关键负结果。

### 2) 四层结构，不止“像导师说话”

| 部分                           | 内容                       | 作用       |
| ---------------------------- | ------------------------ | -------- |
| Part 0 — Method Core         | 任务拆解、优先级、风险分级、兜底策略         | 决定“怎么推进” |
| Part A — Academic Style      | 选题标准、实验规范、论文标准、里程碑、伦理红线 | 决定“做什么”  |
| Part B — Persona             | 语气、反馈方式、决策偏好、关系行为（5 层）    | 决定“怎么说”  |
| Part C — Graduation Playbook | 数据表达优化、故事化写作、最小改动审稿、保底路线  | 决定“怎么过线” |

### 3) 内置毕业场景模板（红线内）

- **数据美化但不造假**：统一展示规范 + 稳健性检验 + 风险披露
- **故事化写作**：证据先行的叙事重排，不夸大贡献
- **最小改动通过审稿**：先改致命项，再改加分项
- **毕业里程碑保底**：最小可交付 + 兜底方案

### 4) 持续进化

- 追加素材：增量 merge，不覆盖历史结论
- 对话纠偏：一句“他不会这样说”立即修正
- 版本管理：备份 / 回滚 / 清理

### 5) 预蒸馏方法论模板

蒸馏时可选三种策略：

- `strict_distill`：仅用用户素材
- `hybrid_distill`：素材 + 预蒸馏模板（推荐）
- `template_first`：模板优先（素材不足场景）

适用于：用户素材少、导师方法论弱、时间紧需要先保底。

### 6) 默认导师（蒸馏版）

仓库内置了基于某位能力很强的🐏导蒸馏的默认模板：

- `defaults/default_advisor_meta.json`
- `defaults/default_method_core.md`
- `defaults/default_advisor_academic.md`
- `defaults/default_advisor_persona.md`
- `defaults/default_advisor_playbook.md`

---

## 安装

仓库地址：`https://github.com/UniversePeak/Supervisor.skill`

### 一键安装/更新（Linux / macOS）

```bash
# Claude Code（全局）
REPO="https://github.com/UniversePeak/Supervisor.skill.git"; TARGET="$HOME/.claude/skills/create-supervisor"; mkdir -p "$(dirname "$TARGET")"; if [ -d "$TARGET/.git" ]; then git -C "$TARGET" pull --ff-only; else git clone "$REPO" "$TARGET"; fi

# Codex（全局）
REPO="https://github.com/UniversePeak/Supervisor.skill.git"; TARGET="$HOME/.codex/skills/create-supervisor"; mkdir -p "$(dirname "$TARGET")"; if [ -d "$TARGET/.git" ]; then git -C "$TARGET" pull --ff-only; else git clone "$REPO" "$TARGET"; fi

# OpenClaw（全局）
REPO="https://github.com/UniversePeak/Supervisor.skill.git"; TARGET="$HOME/.openclaw/workspace/skills/create-supervisor"; mkdir -p "$(dirname "$TARGET")"; if [ -d "$TARGET/.git" ]; then git -C "$TARGET" pull --ff-only; else git clone "$REPO" "$TARGET"; fi
```

### 一键安装/更新（Windows PowerShell）

```powershell
# Claude Code（全局）
$repo="https://github.com/UniversePeak/Supervisor.skill.git"; $target="$HOME\.claude\skills\create-supervisor"; if (Test-Path "$target\.git") { git -C $target pull --ff-only } else { New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null; git clone $repo $target }

# Codex（全局）
$repo="https://github.com/UniversePeak/Supervisor.skill.git"; $target="$HOME\.codex\skills\create-supervisor"; if (Test-Path "$target\.git") { git -C $target pull --ff-only } else { New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null; git clone $repo $target }

# OpenClaw（全局）
$repo="https://github.com/UniversePeak/Supervisor.skill.git"; $target="$HOME\.openclaw\workspace\skills\create-supervisor"; if (Test-Path "$target\.git") { git -C $target pull --ff-only } else { New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null; git clone $repo $target }
```

### 依赖

```bash
pip3 install -r requirements.txt
```

---

## 使用

在 Claude Code / Codex / OpenClaw 中输入：

```text
/create-supervisor
```

按流程完成：

1. 选择工作模式（学术理想型 / 毕业优先型）
2. 选择蒸馏策略（strict / hybrid / template-first）
3. 填写导师基础信息
4. 导入素材
5. 预览确认并生成

### 管理命令

| 命令                                      | 说明           |
| --------------------------------------- | ------------ |
| `/list-supervisors`                     | 列出所有导师 Skill |
| `/{slug}`                               | 完整模式（A+B+C）  |
| `/{slug} proposal`                      | 开题论证         |
| `/{slug} paper`                         | 论文改稿         |
| `/{slug} meeting`                       | 组会问答         |
| `/{slug} rebuttal`                      | 审稿回复         |
| `/{slug} deadline`                      | 进度规划         |
| `/{slug} ethics`                        | 学术伦理检查       |
| `/{slug} career`                        | 升学/就业建议      |
| `/{slug} pragmatic`                     | 毕业场景模板调用     |
| `/update-supervisor {slug}`             | 追加素材并更新      |
| `/supervisor-rollback {slug} {version}` | 回滚历史版本       |

---

## 效果示例

> 输入画像：`某985 计算机学院 博导 带12人 高标准低容错 喜欢说“你要讲一个故事”`

**场景一：选题被打回**

```text
你         ❯ 选题不行吗，该怎么改？

导师.skill  ❯ 
你要造航母搞个大创新？你现在的核心问题是连个完整的 story 都串不起来。
             开题不是罗列技术名词，我提几个问题吧：
             1) 你到底在解决这个领域的什么真实痛点？
             2) 凭什么你的方法能 work？你要能先说服你自己。
             3) 你拿什么指标去对比现有的 Baseline？
```

**场景二：论文改稿**

```text
你         ❯ 你要讲一个故事到底是什么意思啊?

导师.skill  ❯ 你这版稿子太像你的实验记录了，审稿人没有义务透过你密密麻麻的表格去猜你的贡献。
             “你要讲一个故事”，懂吗？
             第一段抛出领域的祖传痛点，第二段点出前人方法哪里不足，第三段顺理成章砸出你的模块。
             把你做的实验用清晰的逻辑包装起来，主线顺不下来，语法改得再漂亮也中不了好会。回去重写引言。
```

**场景三：组会准备**

```text
你         ❯ 下周组会怕讲不清，能给我个模板之类的让我参考不。

导师.skill  ❯ 组会上不要贴满屏的代码，大家的时间都很宝贵，我带这么多人不需要看你证明自己有多辛苦。
             你汇报就控制在三页 PPT：
             - 第一页：上周的计划实现了几成？直接上最好的和最差的结果对比图。
             - 第二页：现在死卡在哪个点上？需要我给你提供什么资源，或者拍板什么方向？
             - 第三页：下周最核心的只做哪两件事？
             讲清这三点就结束，干脆利落一点，把时间留给下一个解决问题的人。
```

## 项目结构

```text
create-supervisor/
├── SKILL.md
├── README.md
├── defaults/
│   ├── default_advisor_meta.json
│   ├── default_method_core.md
│   ├── default_advisor_academic.md
│   ├── default_advisor_persona.md
│   └── default_advisor_playbook.md
├── prompts/
│   ├── intake.md
│   ├── academic_analyzer.md
│   ├── persona_analyzer.md
│   ├── method_core_builder.md
│   ├── academic_builder.md
│   ├── persona_builder.md
│   ├── pragmatic_playbook.md
│   ├── merger.md
│   └── correction_handler.md
├── tools/
│   ├── skill_writer.py
│   ├── version_manager.py
│   └── material_normalizer.py
├── requirements.txt
├── LICENSE
└── .gitignore
```

---

## 注意事项

- 原材料质量决定还原度：批注和真实反馈 > 主观印象
- “毕业优先型”不是学术作弊开关，而是项目管理优先级开关
- 本项目用于学习协作与学术训练，不用于骚扰、隐私侵犯或不当用途

---

## 致敬 & 引用

本项目参考并致敬以下开源工作：

- [同事.skill](https://github.com/titanwings/colleague-skill)
- [老板.skill](https://github.com/nicepkg/boss-skill)
- [前任.skill](https://github.com/therealXiaomanChu/ex-skill)

考虑到在真实的学术生态中，导师与学生的交流往往发生于“组会汇报”或“突击电话”等非结构化的语音场景，纯文本语料很难完整捕捉其精神内核。因此，在同系列 Skill 的基础架构上，本项目新增了全新的预蒸馏层。

不止是导师的语气词、标点符号和画饼习惯。通过这一层的增强，我们旨在重塑并强化你导师的学术指导能力。在赛博空间里，你可以选择同时接受现实世界中的“原生导师”与被强化后的“数字孪生导师”的教导——同宗同源，双倍的快乐。（你可以选择关闭）

为此，以下是底层机制：

Part 0 — Method Core（预蒸馏通用方法论层）：越过表层话术，直接提取导师言语背后的底层学术逻辑与生存法则。

灵活的蒸馏策略路由：内置 strict_distill（严格克隆） / hybrid_distill（混合增强） / template_first（模板接管）三个开关，让你能够根据当前的抗压能力自由调节“赛博导师”的干预程度。

素材评分与“学术扶贫”机制（面向散养/放养场景）：通过语料充分度评分评估蒸馏质量风险。当有效素材不足，或导师语料中能提取出的方法论部分较弱时，系统会优先建议采用 hybrid_distill / template_first 策略，以注入高质量通用方法模板，补齐数字导师的执行能力。（当然，这并不完美）

---

## 给各位研究生和准研究生们的一些话

科研没那么神圣，也没那么不堪。你眼中高高在上的导师，既不是指路明灯，也不是十恶不赦的恶魔。ta 很可能只是一个被职称、基金、中年危机层层裹挟着的、最大号的牛马。每个人的导师都不一样，但作为学生，我们很难真正与之对抗。
若干年后你再回头看时，那些曾经让你夜不能寐的顶刊顶会、SOTA、精心设计的实验，都会在岁月里静静风化成一段不再运行的代码和一堆早已过期的数据。那个因跑不出结果而崩溃的凌晨、那些返修到天亮的夜晚、那些被push到怀疑人生的瞬间，最终都只剩下一张薄薄的学位证。
走出校门的那天，阳光穿过树叶砸在地上，你忽然发觉：自己不过是默默走完了一场没有硝烟的幻灭与和解。
世界中只有一种英雄主义，那就是认清生活的真相后，依然热爱生活。无论遇到怎么样的导师、多苦难的问题，都请把身心健康放在第一位。  
祝你顺利毕业，也祝你前程似锦。
<div align="center">
  <img src="assets/images/scene-1.png" alt="场景截图1" width="48%" />
  <img src="assets/images/scene-2.png" alt="场景截图2" width="48%" />
</div>

<div align="center">
  <img src="assets/images/accept.png" alt="accept截图" width="60%" />
</div>

---

<div align="center">

MIT License © contributors

</div>
