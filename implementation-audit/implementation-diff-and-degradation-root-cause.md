# PPTSmith 实现级差异审计：State of AI 2025 质量降级

- 审计日期：2026-08-05
- TASK_ID：`pptsmith-multi-audience-routing`
- WRITE_ROOT：`/Users/skillmelody/.openclaw/workspace/MeowClawLab/.worktrees/pptsmith-multi-audience-routing`
- 分支 / 基线：`feat/pptsmith-multi-audience-routing` @ `862347f`
- 审计范围：仅比较旧高质量样例的实现路径与新多受众升级路径；不将“成品看起来不同”当作根因。

## 结论（实事求是）

本次质量降级的首要根因已经定位：**新版管线把 visual plan 当成独立的验证/审计产物，而没有把它转换、回写或绑定到最终的 PPT IR 与 delivery plan。**

因此，管线表面上完成了“受众路由、叙事顺序、页面意图、组件选择”的升级；但最终构建器只读取原有 `ppt-ir.json` 内人工预填的 `bar_chart` / `native_table` 对象。它没有收到 visual plan 中的 `phase_roadmap`、`relationship_canvas`、`kpi_dashboard` 等页面意图，也不会因为页面意图而改变布局。

这不是模型理解能力不足，也不是单纯的视觉 QA 不严格；而是 **plan → IR → delivery → renderer 的生产数据流断裂**。新路径的“规划”未成为“构建指令”。

在此之外还存在两个加剧质量退化的实现问题：

1. `python_pptx` adapter 实际只绑定了 6 个通用组件和 6 个新增专项 renderer；研究报告需要的 `flywheel`、`causal_chain`、`data_flow`、`hub_spoke` 等在 capability report 中均为 `unsupported`。旧稿却用直接形状脚本实现了这些表现形式。
2. 标准档未要求基准视觉 rubric / contact-sheet 评分；`visual_revision` 在没有 observations、rubric_score 或 contact_sheet_metrics 时会得到 `no_revision`，即使页面已经被压缩成图表/表格，也不会触发返工。

当前分支还不能宣称“多受众升级稳定完成”：本审计执行的定向测试 `tests/unit/test_visual_planner.py + tests/integration/test_visual_narrative_phase1.py` 结果为 **10 passed, 2 failed**。失败发生于 `resolve_delivery`：`BUILDER_SELECTION_NO_VALID_CANDIDATE`、`CAPABILITY_BUILDER_NOT_FOUND`、`DELIVERY_PLAN_UNSUPPORTED`。

## 对比对象与证据

| 项目 | 旧样例 | 新升级样例 |
|---|---|---|
| PPTX | `deliverables/state-of-ai-2025-deepseek-v4-pro-test/deepseek-state-of-ai-2025.pptx` | `state-of-ai-2025-deepseek-v4-pro-upgrade/delivery/deck.pptx` |
| 构建方式 | 单一、直接的 `build_deepseek_deck.py`，以页面为单位手写原生布局 | `run_pipeline.py` 阶段化通用管线，最终 `PythonPptxAdapter` 由 PPT IR 驱动 |
| 页数 | 14 | 12 |
| 总形状数 | 837（59.8/页） | 70（5.8/页） |
| 文本对象数 | 510 | 46 |
| 原生图表/表格 | 0 / 0（数据图通过形状精细编排） | 7 / 4 |
| 连接器 | 0（旧稿用箭头形状实现关系） | 0 |
| 证据文件 | `old-pptx-object-census.md` | `new-pptx-object-census.md` |

旧稿的 storyboard 明确要求 5 张关系/结构主页面：成熟度流、行业热力矩阵、高绩效者 flywheel、混合智能架构、风险因果链。对应脚本确实逐页用矩形、圆角矩形、箭头、节点和精确位置绘制：共 33 个 `add_rect`、13 个 `add_rounded_rect`、91 个 `add_textbox` 调用。

新稿的 build manifest 却记录 7 个 native chart、4 个 native table、0 connectors；这已经与“关系页必须原生图谱化”的目标矛盾。

## 数据流逐层追踪

### 1. 旧路径：规划直接就是渲染指令

`storyboard.md` → `build_deepseek_deck.py` → `python-pptx` 原生形状

- 每页都有专用的空间结构和对象组合。
- 例如 S08 flywheel 和 S09 layered architecture 在脚本中直接定义中心节点、环形/层级节点、箭头、比较区和注释区。
- 规划与构建没有中间语义丢失层：叙事决定直接以坐标化的对象集合实现。

代价是可复用性低、维护成本高，且旧样例没有当时的真实渲染验证；但它确实兑现了多样的视觉页面。

### 2. 新路径：新增了规划层，但没有进入构建输入

当前新路径：

`source-context brief` → `audience-route` → `storyline` → `visual-plan`  **（断裂）**  `ppt-ir` → `delivery-plan` → `PythonPptxAdapter` → PPTX

可复核证据：

- `run_pipeline.py` 的 `plan_visual_narrative()` 只产出 `contracts/visual-plan.json`。
- 随后的 `resolve_delivery()` 只接收 `ppt-ir.json`、style、registry、capabilities；其 CLI 没有 `--visual-plan` 参数。
- `build()` 同样只接收 `ppt-ir.json`、style、delivery plan；`PythonPptxAdapter.plan()` 只合并 delivery 的对象 route，完全不消费 visual plan。
- 仓库内搜索显示，除 `visual_revision` 的审计逻辑外，没有将 `visual-plan.json` 写入/合并到 PPT IR 的生产转换器。

### 3. 本次样例逐页不一致（直接证据）

| 页 | visual plan 的 semantic component | PPT IR 实际对象 | 是否兑现 |
|---|---|---|---|
| S01 | narrative_statement | 无对象 | 否 |
| S02 | data_comparison_bridge | bar_chart | 否（组件语义未保留） |
| S03 | data_comparison_bridge | bar_chart | 否 |
| S04 | kpi_dashboard | native_table | 否 |
| S05 | relationship_canvas / unsupported | bar_chart | **否，关系页降级为图表** |
| S06 | data_comparison_bridge | bar_chart | 否 |
| S07 | phase_roadmap | native_table | **否，序列页降级为表格** |
| S08 | kpi_dashboard | bar_chart | 否 |
| S09 | data_comparison_bridge | bar_chart | 否 |
| S10 | relationship_canvas / unsupported | bar_chart | **否，关系页降级为图表** |
| S11 | data_comparison_bridge | native_table | 否 |
| S12 | phase_roadmap | native_table | **否，收口行动页降级为表格** |

这 12 页中，没有一页的 `semantic_component` 被写成 PPT IR 对象的 `component_type`。所以 visual-plan schema 验证通过，并不表示成品兑现了视觉计划。

## 实现差异与质量退化机制

### A. 视觉计划与 PPT IR 脱钩（根因，P0）

**实现事实**：planner 可选择 `phase_roadmap`、`relationship_canvas` 等；renderer 仅从 PPT IR 的 `objects[]` 获取 component type。中间无 compile step。

**后果**：新加入的八路线叙事规则只约束了 `storyline.narrative_stage` 的顺序，无法约束组件、布局或实际页面表达。任何在 PPT IR 中预先写成 bar chart 的页面都仍然是 bar chart。

**修复目标**：新增唯一的 `compile_visual_plan_to_ppt_ir` 阶段，必须在 `plan_visual_narrative` 后、`resolve_delivery` 前运行，并且：

- 按 slide ID 将 `semantic_component`、`primary_expression`、`page_archetype`、`layout`、`density`、`delivery` 写入 PDI；
- 将可渲染的语义组件编译为 PPT IR `objects[]`（而不是只留一份旁路 JSON）；
- 对 `unsupported` relationship canvas 直接 fail-closed；不得静默保留 chart/table；
- 为每张关键页面生成 `planned_component == actual_component` 的 bind record；build 后通过 inspection / manifest 核验。

### B. component registry 的“声明能力”超过实际 renderer binding（P0）

**实现事实**：registry 列有许多关系组件，但 `_RENDERER_BINDINGS` 对 `python_pptx` 实际只有：comparison/metric/summary card、bar chart、process flow、table、heat matrix、layered architecture、drill-down stair、phase roadmap、product UI、interaction storyboard。

**缺口**：此次研究报告需要的 flywheel、causal chain、data flow 等要么在 capability report 中 `unsupported`，要么并未从 visual plan 编译到 IR。新构建器也没有通用 `relationship_canvas` handler。

**后果**：即使连接上 plan→IR，研究型关系页面仍无法可靠渲染；当前可能会被通用对象替代，或因适当的 fail-closed 而停止。

**修复目标**：先只实现本报告必需的三种最小组件，并以真实页面对象测试：

1. `flywheel`：中心结论、4–6 节点、定向箭头、比较/证据侧栏；
2. `causal_chain`：因果节点 + 显式箭头 + consequence/mitigation 双列；
3. `research_maturity_flow`（或将现有 `phase_roadmap` 扩展）：阶段节点、规模断点、证据标注。

不要先做一堆 registry 声明；每个新增组件都要有 binding、schema、smoke、真实 deck 覆盖、LibreOffice 渲染和对象 readback。

### C. builder selection 在标准档接受不完整的路由覆盖（P0）

**实现事实**：此次强制 `python_pptx` 后 build manifest 仍给出 `fallback_count: 7`、`native_component_coverage: 0.6818`；但 `resolve_delivery()` 只检查 PPT IR 已有对象是否可交付，未检查 visual plan 所要求的语义组件。

**后果**：选择器对“表格/条形图可生成”打分，绕开了“关系页应该是什么”的问题；实际构建从来没有被要求覆盖 visual plan。

**修复目标**：compile 后，以 compiled IR 与 visual-plan bind record 进行 builder selection；标准档若存在 key 关系页且 builder 不支持，直接拒绝，而不是由调用方强制 builder 继续构建。

### D. style contract 被 adapter 大量忽略（P1）

**实现事实**：本次 build manifest 记录数十项 `Unsupported style field ignored by PythonPptxAdapter`，包括 grid、spacing、card tokens、diagram tokens、chart tokens、typography、颜色层级等。

**后果**：虽然 planner 选择 `azure-insight-architecture`，最终 adapter 实际仅消费少量默认标题、正文、边距和基础色；无法兑现该视觉系统的网格、密度、图表、连接器和卡片设计。

**修复目标**：将 style contract 拆为“必消费字段”与“可选字段”。standard/premium 不允许关键字段被 ignored：grid、title/body/footnote typography、chart tokens、diagram tokens、spacing、surface palette。未消费应为 build fail，不只是 warning。

### E. 视觉 QA 没有输入，也没有与成品关联（P1）

**实现事实**：`visual_revision()` 只有在 storyline 提供 `revision_observations`、`rubric_score` 或 `contact_sheet_metrics` 时才有动作。本次没有这些输入，因此生成 `no_revision`。而 `production-profile.json` 是 `standard`，允许跳过 `full_render` 与 `benchmark`。

**后果**：LibreOffice 的“非空白页”检测与结构 QA 无法发现“关系页被表格替代”“视觉节奏过度单一”。

**修复目标**：对于八路线验收样例，强制至少一轮自动 contact-sheet 指标 + 独立人工/模型视觉 rubric；但视觉 QA 应在 plan-to-IR binding 修复之后启用，否则它只能反复发现症状，不能修复断点。

## 尚不能断言的事项

- 不能仅凭旧稿对象更多就宣布它全面更好；它是专用脚本，数据图不是原生 `Chart` 对象，且当时报告注明无真实 LibreOffice 渲染。
- 不能把此次问题归咎于 DeepSeek-V4-Pro。模型规划内容不等于构建器执行结果；当前证据已定位为编译/绑定链路缺失。
- 不能在未给研究型关系组件补齐真实 binding 前承诺“新 Skill 已达到旧稿视觉质量”。

## PMO 专业生产包复核与统一能力决策

月主已明确：**不再按免费版 / 付费版拆分 PPT 核心生成质量。** 此后若 PMO 中的能力经验证可用且能提升通用产出质量，应迁入同一套 PPTSmith 引擎与质量门禁；差异只能存在于服务、支持、部署或交付方式，不能存在于核心 renderer、页面质量或 QA 能力。

### 已核验的 PMO 实现

只读检查位置：

`/Users/skillmelody/.openclaw/workspace/private-artifacts/pptsmith-pmo-consulting-pack/`

真实存在并可检查的实现包括：

- `scripts/build_pmo_deck.py`：PMO domain JSON 到原生 PowerPoint 的直接 Python renderer；
- `scripts/verify_pmo_deck.py`：结构检查、LibreOffice 渲染、原生对象数量和图片对象检查；
- 10 类页面：Executive Dashboard、Roadmap、Milestone、RAID、Workstream、RACI、Risk Heat Map、Decision、KPI、Action Tracker；
- 复核样例 `output/ai-platform-project-pmo.pptx` 的 README 记录：11 页、274 原生形状、23 原生连接器、1 原生图表、0 图片，LibreOffice 11/11 通过；
- Wave E 决策支持样例的 README 记录：18 页经 1920×1080 渲染复核，包含决策漏斗、桥接图、门禁路径、矩阵/排序、依赖甘特、约束网络、瀑布、泳道和治理时间线。

这说明 PMO 包不是空概念；其直接 renderer 确实拥有比当前通用 adapter 更成熟的**页面家族、对象组合、连接器、空间布局与视觉验收资产**。

### 不能原样搬入的部分

PMO 包当前仍是：

`PMO domain JSON → 私有 direct renderer → PPTX`

它尚未完成 README 中目标架构的：

`PMO domain JSON → PPTSmith PPT IR / Diagram IR → Delivery Plan → Builder → QA`

此外，把 McKinsey 的研究报告人工改写成 PMO JSON 后，曾产生 RAID、RACI、Action Tracker 等页面。它们对于“企业 AI 推进方案”可作为后续执行转译，但不能自动被当作研究报告原始结论，否则会把研究叙事硬套成项目治理叙事。

因此，不能把整个 PMO deck builder 直接设为所有材料的默认构建器，也不能将 PMO 页面强行注入 research_insight 路线。

### PMO、咨询叙事与公共组件：迁移前的分类结论

**PMO 不是“麦肯锡咨询类 PPT”的同义词。**

- **PMO** 是项目/项目群/组合治理的业务语境：它处理里程碑、工作流、风险、责任、决策、行动与状态。
- **麦肯锡式咨询**是面向管理层的论证和决策支持叙事：结论先行、证据支撑、选项取舍、行动收束。它可以使用 PMO 页面，也可以完全不使用。
- 因此，现有 PMO 包中“咨询风格”来自其视觉语言和表达规范，不能反向推出每一张 PMO 页都只适用于咨询，也不能反向将所有咨询材料都路由为 PMO。

迁移时必须以**页面表达的语义能力**分类，而不是按 PMO 包的历史归属分类：

| 分类 | 可作为统一公共组件 | 适用条件 |
|---|---|---|
| 通用关系/时间表达 | roadmap、milestone timeline、dependency Gantt、swimlane、KPI-status dashboard、risk heat map、decision comparison | 材料中存在阶段、时间、依赖、责任、状态、风险、选择或指标等明确证据；由所有路线按需调用 |
| PMO 专用语义页面 | RAID register、RACI matrix、action tracker、workstream governance board | 仅当材料确有项目治理对象、owner/责任分配、行动期限、风险登记等字段；不可从研究结论或战略报告中臆造 |
| 咨询/研究专用叙事页面 | issue tree、bridge、maturity flow、benchmark comparison、flywheel、causal chain、operating-model architecture | 仅当材料能支撑诊断、因果、成熟度、比较或经营机制；不等于 PMO |

**实施前硬门：**每一个准备迁入的 PMO renderer 都必须先登记其 `semantic_capabilities`、适用 route、所需证据字段、禁止路由与不可自动推断字段。无法通过分类的组件不得迁入默认组件池。

### 正确的统一迁移方案

1. **迁移可复用视觉原语和页面家族，不迁移付费/私有分层。**
   - 高优先级：roadmap / milestone timeline / KPI-status dashboard / risk heat map / decision comparison / workstream swimlane / dependency Gantt。
   - 它们应成为统一 component registry 的真实 `python_pptx` renderer，而不是私有脚本专属能力。

2. **按语义路由调用，不按商业版本调用。**
   - `project_governance`：完整 PMO 页面族可用；
   - `strategic_decision`：可用 decision、KPI、roadmap，但必须有输入证据；
   - `research_insight`：可用趋势、成熟度流、热力图、flywheel、因果链；只有当材料明确转入执行方案时才可调用 roadmap/decision；
   - `product_prd` / `technical_architecture`：只调用适配的 UI、状态链、架构、数据流组件。

3. **通过统一的 plan→IR 编译层进入同一 builder 与 QA。**
   PMO 组件必须具备 schema、IR compiler、renderer binding、capability probe、smoke、真实样例、render/readback；不得再保留“私有脚本绕过通用管线，公开版走简化管线”的质量断层。

4. **优先级调整。**
   H1（visual-plan → PPT IR binding）仍然是第一步；完成后，先迁入 PMO 已成熟且与 H1 验证兼容的 `phase_roadmap` / milestone 语义页面，再根据研究报告补齐 flywheel / causal chain。不要先把整套 PMO renderer 大搬家。

## 单点修复顺序（避免死循环）

### 假设 H1

如果在 delivery resolution 之前把 visual plan 编译并绑定为 PPT IR 对象，并且对 visual-plan/PPT-IR component mismatch fail-closed，那么本次样例不可能再在 S05/S07/S10 静默生成 bar chart/table。

### 最小验证

1. 新增一个失败测试：给包含 `phase_roadmap`、`relationship_canvas` 的 visual plan + 不匹配 PPT IR，要求 pipeline 在 `compile_visual_plan_to_ppt_ir` 或 `resolve_delivery` 失败，错误码 `VISUAL_PLAN_IR_COMPONENT_MISMATCH`。
2. 仅实现 phase_roadmap 的 compile/bind（已有 verified renderer），并用一个 3 页最小 fixture 验证：visual plan → IR object type → delivery selected route → builder actual route 都是 `phase_roadmap/native_diagram`。
3. 运行该 fixture 的实际 LibreOffice 渲染与 object inspection；通过后才处理 flywheel/causal chain。

### 禁止事项

- 不重跑 State of AI 全 deck 来“碰碰运气”。
- 不通过修改 PPT 成品坐标来掩盖管线断裂。
- 不把 `relationship_canvas` 继续静默映射为 bar chart、表格或 generic cards。
- 在 H1 未验证前，不继续新增八条路线的页面原型或做大规模重构。

## 本审计的验证记录

- 路径门禁：`EXECUTION_PATH_OK task=pptsmith-multi-audience-routing`。
- 旧/新 PPTX 已直接 readback，object census 已保存。
- 新样例 contracts、logs、builder capabilities、build manifest 与 Python adapter 已读取。
- 定向测试命令：

```bash
python3 -m pytest -q tests/unit/test_visual_planner.py tests/integration/test_visual_narrative_phase1.py
```

结果：`10 passed, 2 failed in 99.80s`。

失败用例：

- `test_visual_narrative_stages_run_before_delivery_resolution`
- `test_visual_revision_is_applied_at_most_once_and_keeps_first_pass_evidence`

共同失败原因：`resolve_delivery` 返回 `BUILDER_SELECTION_NO_VALID_CANDIDATE, CAPABILITY_BUILDER_NOT_FOUND, DELIVERY_PLAN_UNSUPPORTED`。

## 当前状态

- 根因定位：完成。
- PMO 包复核：完成；确认其可复用专业组件应迁入同一质量引擎，但不能将 PMO 专用 deck builder 直接作为所有文档的默认生成器。
- 修复：H1 的第一最小闭环已完成：`compile_visual_plan.py` 在 `plan_visual_narrative` 后、`resolve_delivery` 前把 `phase_roadmap` 编译到 PPT IR；对应 roadmap renderer 的里程碑字号已提升至 10.5pt 以满足 style minimum。对未实现关系组件，产品策略改为**显式原生占位**而非失败或静默降级：编译器生成 `comparison_card`，标记 `component_status=unsupported_placeholder`，在 PPT 中说明应展示的关系图、未展示原因及“联系 MeowClaw / PPTSmith 团队专项优化”；build manifest 记录 `unsupported_placeholder_count`。验证：占位定向测试 `1 passed`；完整定向集 `15 passed in 114.71s`（visual planner、phase roadmap renderer、visual narrative integration）。尚未重跑 State of AI 全 deck，尚未迁入其他 PMO 页面家族。
- 唯一主交付物：本报告。
