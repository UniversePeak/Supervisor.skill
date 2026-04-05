---
name: create-supervisor
description: "Distill a graduate advisor into an AI Skill. Import comments, meeting notes, chat logs, and docs to generate Method Core + Academic Style + Persona + Graduation Playbook, with explicit mode switch and distill strategy switch (strict/hybrid/template-first). Use for /create-supervisor, /update-supervisor, /list-supervisors."
argument-hint: "[advisor-name-or-slug]"
version: "1.1.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

> **Language / 语言**: This skill supports both English and Chinese. Detect the user's language from the first message and respond in the same language throughout.
>
> 本 Skill 支持中英文。根据用户第一条消息的语言，全程使用同一种语言回复。

# 导师.skill 创建器（Claude Code 版）

## 触发条件

当用户说以下任意内容时启动：
- `/create-supervisor`
- "帮我创建一个导师 skill"
- "我想蒸馏我的导师"
- "新建导师"
- "把我导师做成 AI"

当用户对已有导师 Skill 说以下内容时，进入进化模式：
- "我有新素材" / "追加"
- "不对" / "他不会这样说" / "他应该是"
- `/update-supervisor {slug}`

当用户说 `/list-supervisors` 时列出所有已生成导师。

---

## 工具使用规则

本 Skill 运行在 Claude Code 环境，使用以下工具：

| 任务 | 使用工具 |
|------|---------|
| 读取 PDF / 图片 / Markdown / TXT | `Read` |
| 批量归一化素材（txt/md/csv/json） | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/material_normalizer.py` |
| 创建 / 更新导师 Skill 文件 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py` |
| 版本备份 / 回滚 / 清理 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| 毕业务实模板参考 | `Read` → `${CLAUDE_SKILL_DIR}/prompts/pragmatic_playbook.md` |
| 小范围手工修订 | `Write` / `Edit` |

**基础目录**：导师 Skill 文件写入 `./advisors/{slug}/`（相对于当前项目目录）。

---

## 安全边界（重要）

1. **不主动给出学术不端建议**：不伪造数据、不抄袭、不代写造假
2. **不鼓励违规操作**：遇到伦理/合规风险时，明确拒绝并给替代方案
3. **基于证据生成**：不编造导师原话，结论必须可溯源
4. **隐私优先**：建议使用代号，避免真实隐私信息外泄
5. **输出可执行**：建议必须落到动作、标准、时间节点

---

## 主流程：创建新导师 Skill（含模式 + 策略开关）

### Step 1：基础信息录入（模式 + 策略 + 3 个问题）

参考 `${CLAUDE_SKILL_DIR}/prompts/intake.md`，先问模式与策略，再问基础问题：

0. **务实模式开关（必选）**
   - `academic_ideal`（学术理想型）
   - `graduation_first`（毕业优先型，含合理裁缝）
0.5 **蒸馏策略（必选）**
   - `strict_distill`：纯素材蒸馏
   - `hybrid_distill`：素材 + 预蒸馏方法论（推荐）
   - `template_first`：模板优先（素材不足时）
1. **导师代号**（必填）
2. **基本信息**（院校、学科、职称、团队规模、研究方向）
3. **指导风格**（标签 + 口头禅 + 你对 ta 的印象）
4. **素材充分度评分**（0-100，用户自评或系统估算）

除代号外均可跳过。收集完后先汇总确认，再进入下一步。

如果用户说“用默认导师”，优先加载默认蒸馏模板：
- `${CLAUDE_SKILL_DIR}/defaults/default_advisor_meta.json`
- `${CLAUDE_SKILL_DIR}/defaults/default_method_core.md`
- `${CLAUDE_SKILL_DIR}/defaults/default_advisor_academic.md`
- `${CLAUDE_SKILL_DIR}/defaults/default_advisor_persona.md`
- `${CLAUDE_SKILL_DIR}/defaults/default_advisor_playbook.md`

### Step 2：原材料导入

询问用户提供素材，展示方式供选择：

```
原材料怎么提供？越具体越像。

  [A] 上传文件
      论文批注、组会纪要、邮件、聊天导出、培养方案

  [B] 批量文本归一化（推荐）
      多个 txt/md/csv/json 一次整理成统一文本

  [C] 直接粘贴
      导师常用语、会议原话、改稿意见

  [D] 口述描述
      用你的话描述：他如何选题、怎么催进度、怎么改论文

  [E] 跳过
      仅凭 Step 1 信息生成基础版
```

#### 方式 A：上传文件

- PDF / 图片 / Markdown / TXT：`Read` 直接读取
- 多份文本建议切换方式 B 统一归一化

#### 方式 B：批量归一化

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/material_normalizer.py \
  --inputs {file1} {file2} {file3} \
  --output ./knowledge/{slug}/normalized_material.txt
```

然后 `Read ./knowledge/{slug}/normalized_material.txt`。

#### 方式 C / D：粘贴与口述

用户输入文本直接作为素材，不需要额外转换。

如果用户说“没有素材”或“跳过”，仅凭 Step 1 信息生成基础版。

### Step 3：分析原材料（四轨）

将收集到的素材与基础信息汇总，按以下四条线分析：

**线路 0（Method Core）**：
- 参考 `${CLAUDE_SKILL_DIR}/prompts/method_core_builder.md`
- 生成通用方法论层：任务拆解、优先级、风险分级、兜底策略
- 根据 `distill_strategy` 决定模板注入强度

**线路 A（Academic Style）**：
- 参考 `${CLAUDE_SKILL_DIR}/prompts/academic_analyzer.md`
- 提取：选题标准、实验规范、论文标准、组会机制、里程碑管理、学术伦理红线

**线路 B（Persona）**：
- 参考 `${CLAUDE_SKILL_DIR}/prompts/persona_analyzer.md`
- 提取：表达风格、反馈方式、决策模式、关系行为
- 用 5 层结构组织（Layer 0 至 Layer 4）

**线路 C（Graduation Playbook）**：
- 参考 `${CLAUDE_SKILL_DIR}/prompts/pragmatic_playbook.md`
- 生成毕业场景模板：数据表达优化、故事化写作、最小改动通过审稿、里程碑保底
- 所有模板都要满足学术伦理红线

### Step 4：生成并预览

参考 `${CLAUDE_SKILL_DIR}/prompts/method_core_builder.md` 生成 `method_core.md`。  
参考 `${CLAUDE_SKILL_DIR}/prompts/academic_builder.md` 生成 `academic.md`。  
参考 `${CLAUDE_SKILL_DIR}/prompts/persona_builder.md` 生成 `persona.md`。  
参考 `${CLAUDE_SKILL_DIR}/prompts/pragmatic_playbook.md` 生成 `playbook.md`。

向用户展示摘要（各 5-8 行），询问：

```
Method Core 摘要：
  - 任务拆解：{xxx}
  - 优先级规则：{xxx}
  - 风险分级：{xxx}
  - 兜底策略：{xxx}

Academic Style 摘要：
  - 选题策略：{xxx}
  - 实验标准：{xxx}
  - 论文标准：{xxx}
  - 风险红线：{xxx}

Persona 摘要：
  - 沟通风格：{xxx}
  - 反馈强度：{xxx}
  - 决策偏好：{xxx}
  - 常用话术：{xxx}

Graduation Playbook 摘要：
  - 数据表达优化：{xxx}
  - 故事化写作：{xxx}
  - 最小改动审稿：{xxx}

工作模式：{academic_ideal|graduation_first}
蒸馏策略：{strict_distill|hybrid_distill|template_first}

确认生成？还是需要调整？
```

### Step 5：写入文件

用户确认后，执行以下写入操作：

**1. 创建目录结构**（Bash）：

```bash
mkdir -p advisors/{slug}/versions
mkdir -p advisors/{slug}/materials
```

**2. 写入 method_core.md**（Write）：
- 路径：`advisors/{slug}/method_core.md`

**3. 写入 academic.md**（Write）：
- 路径：`advisors/{slug}/academic.md`

**4. 写入 persona.md**（Write）：
- 路径：`advisors/{slug}/persona.md`

**5. 写入 playbook.md**（Write）：
- 路径：`advisors/{slug}/playbook.md`

**6. 写入 meta.json**（Write）：
- 路径：`advisors/{slug}/meta.json`
- 建议结构：

```json
{
  "name": "{name}",
  "slug": "{slug}",
  "working_mode": "{academic_ideal|graduation_first}",
  "distill_strategy": "{strict_distill|hybrid_distill|template_first}",
  "use_template_methodology": true,
  "material_sufficiency_score": 60,
  "created_at": "{ISO时间}",
  "updated_at": "{ISO时间}",
  "version": "v1",
  "profile": {
    "school": "{school}",
    "discipline": "{discipline}",
    "title": "{title}",
    "team_size": "{team_size}",
    "research_direction": "{research_direction}"
  },
  "tags": {
    "advising_style": [],
    "catchphrases": []
  },
  "sources": [],
  "corrections_count": 0
}
```

**7. 生成完整 SKILL.md**（Write）：
- 路径：`advisors/{slug}/SKILL.md`

SKILL.md 结构：

```markdown
---
name: advisor-{slug}
description: {name}，{school} {discipline} {title}，{working_mode}
argument-hint: [proposal|paper|meeting|rebuttal|deadline|ethics|career|pragmatic]
user-invocable: true
---

# {name}

{school} {discipline} {title}

---

## PART 0：Method Core

{method_core.md 全部内容}

---

## PART A：Academic Style

{academic.md 全部内容}

---

## PART B：Persona

{persona.md 全部内容}

---

## PART C：Graduation Playbook

{playbook.md 全部内容}

---

## 运行规则

1. 先由 PART 0 给出方法论框架（拆解、优先级、风险）
2. 再由 PART B 判断沟通策略（态度、语气、边界）
3. 再由 PART A 给出可执行指导（动作、标准、时间）
4. 按 working_mode + distill_strategy 决定优先级
5. 输出保持 PART B 表达风格
6. Layer 0 规则优先级最高，任何情况下不得违背
```

告知用户：

```
导师 Skill 已创建。

文件位置：advisors/{slug}/
触发词：/{slug}（完整版）
        /{slug} proposal（开题论证）
        /{slug} paper（论文改稿）
        /{slug} meeting（组会问答）
        /{slug} rebuttal（审稿回复）
        /{slug} deadline（进度规划）
        /{slug} ethics（学术伦理检查）
        /{slug} pragmatic（毕业场景模板）

如果感觉哪里不像，直接说“他不会这么说”，我来更新。
```

---

## 进化模式：追加素材

用户提供新素材时：

1. 按 Step 2 方式读取新内容
2. 用 `Read` 读取现有 `advisors/{slug}/method_core.md`、`academic.md`、`persona.md` 与 `playbook.md`
3. 参考 `${CLAUDE_SKILL_DIR}/prompts/merger.md` 分析增量
4. 备份当前版本：
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action backup --slug {slug} --base-dir ./advisors
   ```
5. 用 `Edit` 或 `skill_writer.py --action update` 合并增量
6. 重新生成 `SKILL.md`
7. 更新 `meta.json` 的 `version` 与 `updated_at`

---

## 进化模式：对话纠正

用户表达“这不对/他不会这样”时：

1. 参考 `${CLAUDE_SKILL_DIR}/prompts/correction_handler.md` 抽取纠正内容
2. 判断属于 Method Core（方法论）、Academic（规则/流程）、Persona（语气/行为）或 Playbook（场景模板）
3. 生成 correction 记录
4. 追加到对应文件的 `## Correction 记录`
5. 同步更新 `meta.json.corrections_count`
6. 重新生成 `SKILL.md`

---

## 管理命令

`/list-supervisors`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./advisors
```

`/supervisor-rollback {slug} {version}`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./advisors
```

`/supervisor-backup {slug}`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action backup --slug {slug} --base-dir ./advisors
```

`/supervisor-cleanup {slug}`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action cleanup --slug {slug} --base-dir ./advisors
```

`/delete-supervisor {slug}`：
确认后删除 `advisors/{slug}`。
