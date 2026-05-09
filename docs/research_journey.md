# AutoSim 调研历程与方案演化记录

> **时间跨度**：2026-05-08 ~ 2026-05-09（约 1.5 天）
> **总投入**：6 轮调研 / 15 个并行 agent 调研任务（13 成功，2 因配额限制失败）/ 4 轮架构反转 / 2 轮落地 sanity check
> **终点**：方向锁定 v4-final，0 个 RED 阻断，2 个 YELLOW 已识别并缓解
> **原始 agent 报告位置**：`C:\Users\elane\AppData\Local\Temp\claude\E--test-AutoSim\db396173-c3c7-4b90-ade9-db8421856acc\tasks\`

本文档记录"为什么是 v4-final 而不是其他"——每一轮调研触发的反转、每一个被排除的方案的具体证据、每一个决策的当时上下文。任何对 v4-final 的修订建议要先读本文。

---

## 1. 项目背景与初始约束

### 用户原始需求（2026-05-08 起）

- **目标**：纯视觉端到端自动驾驶**闭环**仿真器
- **背景**：中国城市
- **车辆模型**：运动学（不用动力学）
- **技术兴趣**：Nvidia 世界模型方向（Cosmos 系列）

**落地用例**：
1. 编辑各种 case
2. 替换端到端自动驾驶算法
3. 同算法跑多 case / 同 case 跑多算法的测试矩阵
4. 高质量视频数据
5. 可落地的 sim2world

### 用户在调研过程中追加的约束（按时间）

| 时间 | 约束 | 影响 |
|---|---|---|
| 2026-05-08 起步 | 算力可走云端 | 解锁 H100、Cosmos、3DGS 重建等大模型 |
| 2026-05-08 起步 | 数据只能用公开数据集 | 排除自采数据，专攻 ONCE/DAIR-V2X/ApolloScape/DrivingDojo |
| 2026-05-08 第 2 轮 | 街景数据可否用？ | 调研后排除商业街景（百度/高德/腾讯 ToS）；Mapillary 唯一 CC BY-SA 干净 |
| 2026-05-09 第 4 轮 | **跑仿真测试可以不用实时，只要看最后的测试报告** | **架构层解放**：Cosmos / VLM E2E / 慢渲染重建全部可用 |
| 2026-05-09 v4-final | UE5 + UE4 都做 | CARLA 双轨道（0.9.16 + 0.10） |
| 2026-05-09 v4-final | 自研非商用 | CC-BY-NC / OML / 出口管制不再约束 |
| 2026-05-09 v4-final | 避免数据申请不通过的风险 | nuScenes mini + DrivingDojo HF 作免审批 MVP |

---

## 2. 调研方法论

### 工具栈

- **并行 background agents**（general-purpose subagent_type）：每个 agent 独立任务，无对话上下文，输入是自包含的 prompt
- **Web 工具**：WebSearch / WebFetch / Read（只读）
- **每 agent 输出预算**：500–1500 字结构化报告 + 来源链接

### 设计原则

1. **每轮只问 3–4 个问题**，避免 agent 失焦
2. **必要事实必须给链接**（GitHub URL / arxiv ID / commit 日期 / issue 编号）
3. **明确"信息缺口"标注**——agent 不能用"应该""估计"含糊
4. **评级强制**：GREEN / YELLOW / RED 必须落到具体证据
5. **死胡同必须保留退出原因**——避免后续重复探索

---

## 3. 六轮调研详细记录

### 第 1 轮：初始 SOTA 画像（4 个并行 agent）

**触发时间**：2026-05-08 上午
**目标**：把整个领域的 SOTA 画一遍，决定技术大方向

| Agent | 任务 | 关键发现 |
|---|---|---|
| #1 | 生成式世界模型仿真 | DriveDreamer4D / ReconDreamer (CVPR'25) 已是 4DGS+生成的混合范式；Cosmos-Predict2.5 唯一商用可控大底座；DriveArena (上海AI Lab) 已有完整 HDMap 闭环 |
| #2 | 3DGS/NeRF 闭环重建 | NVIDIA Omniverse NuRec 于 2026-03 GTC GA；CARLA 0.9.16 已官方集成 NuRec API；DriveStudio/OmniRe (ICLR'25 spotlight) 多数据集统一管线 |
| #3 | 端到端算法接口 | UniAD/VAD/SparseDrive/Hydra-NeXt/DiffusionDrive 都输出 K×3 轨迹，可统一 Plugin Protocol；DriveArena (上海AI Lab) 提供中国 HDMap 闭环 |
| #4 | 数据集 + 仿真器 | NVIDIA AlpaSim 开源闭环框架（声称）；OpenDriveLab WorldEngine 是国内对标；DrivingDojo 解决"中国数据稀缺" |

**v1 架构产出**：AlpaSim 主 + SimScale 反应式 agent 补 + NuRec 渲染 + DriveStudio + ReconDreamer 混合栈

**v1 隐患**：
- ❌ NuRec 真实开源粒度未核实
- ❌ AlpaSim 第三方 planner 接入未文档化的隐患未发现
- ❌ SimScale 实际是 sim-real 训练辅助框架（被误读为 agent 框架）
- ❌ DriveArena 半停滞未发现

---

### 第 2 轮：NuRec / AlpaSim 深挖 → v1→v2 反转

**触发时间**：2026-05-08 下午
**用户提问**：要求确认 NuRec 与 AlpaSim 真实开源状态

| Agent | 任务 | 致命发现 |
|---|---|---|
| #5 | NuRec 开源与重建管线深挖 | **NuRec 实质闭源**：训练管线 + Fixer + 推理服务全是商业 docker `nvcr.io/nvidia/nre/nre-ga`；918 个预训练资产 NVIDIA AV License + 12 月期限 + 不可再分发 + 全欧美；CARLA 0.9.16 集成是商业 plugin，官方 tutorial 当前 broken (CARLA #9667)；论坛已报 "Payment Required" 错误 |
| #6 | AlpaSim 项目深挖 | **AlpaSim 真开源**（NVlabs/alpasim, Apache-2.0, ~1k★）但 918 场景全欧美；**第三方 planner 接入官方未文档**；外部独立复现报告 0 条；只有 NVIDIA 自家 0.81 分基线 |

**v1→v2 触发**：NuRec 不可用 → 渲染层必须自建；AlpaSim 单独不能撑起整个项目

**新发现**：**WorldEngine (OpenDriveLab) 是当下唯一独立可跑的开源闭环**（claim），3DGS 已集成

**v2 架构产出**：WorldEngine 主 + AlpaSim 副 + DriveStudio + gsplat 渲染

**额外修正**：
- DAIR-V2X 因路端固定相机非 ego-centric → 不适合作重建主源
- SimScale 重新定位为 sim-real 训练辅助（不是 agent / 仿真器）

---

### 第 3 轮：WorldEngine + GS 渲染栈 + CARLA → v2→v3 反转

**触发时间**：2026-05-08 傍晚
**用户提问**：调研 WorldEngine、AlpaSim 渲染替代、CARLA case 编辑

| Agent | 任务 | 致命发现 |
|---|---|---|
| #7 | WorldEngine 深度调研 | **WorldEngine 是 vapor 风险高**：建仓 2026-04-10 仅 15 commits / 289★ / 1 个未解 8-GPU bug；**实际是 NAVSIM v2 后训练 demo**——4 秒 pseudo-closed-loop 不是几十秒真闭环；**硬绑 nuPlan**（MTGS 校准、scenario schema、PDM 评测全为 nuPlan 量身）；**arXiv 截至 2026-05-08 未发布**；改造成中国数据 ≥2 个月 |
| #8 | 开源 GS 渲染栈对比 | **gsplat 1.5+ (3DGUT 模式) 是 NuRec 算法核**且完全开源（Apache, 5k★）；一行 API `rasterization(with_ut=True)` 即作渲染服务；H100 ~80 FPS @ 6×720p；DriveStudio + OmniRe (MIT) 是配套训练管线 |
| #9 | CARLA case 编辑角色 | CARLA 是**唯一支持 OSC 1.x 和 2.0 的开源仿真**；Bench2Drive 220 case + Leaderboard 2.0/2.1 = 端到端社区最大 case 库；**官方已把"逻辑/渲染解耦"做成产品路线**（NuRec gRPC 协议 protobuf 已公开） |

**v2→v3 触发**：WorldEngine 不能作主骨架；CARLA 反而是更好的 case 编辑层

**v3 架构产出**：CARLA headless（OSC 2.0 + ScenarioRunner）+ gsplat 主 renderer + DriveStudio 训练 + Cosmos alternative renderer + HUGSIM 评测脚手架

**关键决策**：
- D5 case 编辑 = OSC 2.0 + ScenarioRunner（继承 Bench2Drive 220）
- D6 渲染路由 = fork NuRec gRPC protobuf

---

### 第 4 轮：Cosmos + NAVSIM v2/VLM → v3→v4 反转

**触发时间**：2026-05-09
**用户新约束**：**仿真测试可以不用实时，只要测试报告**——这条约束改变一切

| Agent | 任务 | 关键发现 |
|---|---|---|
| #10 | Cosmos 作主渲染的批跑可行性 | OML 商用 OK，输出物 NVIDIA 不主张所有权，81k 数据集 CC BY 4.0；**单段 121 帧 (~5s) 硬上限**，30s+ 闭环要 chunk；中国感未确认（DrivingDojo LoRA 配方搜不到，需自做）；**出口管制风险**："comply with all applicable export…sanctions laws"——商业落地需法务复核；**Vista (Apache 2.0) 是最干净 fallback** |
| #11 | 离线批跑评测范式 + VLM E2E | **NAVSIM v2 是 2026 离线批跑事实标准**：4 秒 pseudo-closed-loop + EPDMS 报告；2026 SOTA 全在这刷榜（SparseDriveV2 92.0 PDMS / HiST-VLA 88.6 EPDMS / OneVL 88.84）；放开延迟后**单系统 VLM 比 dual system 高 2–4 分**；**Senna (华科+地平线) 完整开源代码+权重** |

**v3→v4 触发**：
1. NAVSIM v2 协议天然对齐"离线 + 测试报告"目标
2. Cosmos 离线下变可行（latency 不再是死结）
3. VLM/VLA 在不要求实时下成 SOTA
4. **gRPC bridge 复杂度归零**（离线让 IPC 简化为 Python ABC）

**v4 架构产出**：CARLA + 三 renderer 对照（CARLA UE / Cosmos / gsplat）+ Senna 主 + SparseDriveV2 副 + NAVSIM v2 metric + HUGSIM 副线

**用户在第 4 轮加问**：
- "如果只是做 case 是不是用不着 carla？" → 回答：保留 CARLA（OSC 2.0 解析 + Bench2Drive case + scenario dump 三件事）
- "保留 CARLA UE 渲染作为对比？" → 答应，三 renderer 升四 renderer

---

### 第 5 轮：CARLA 替代 + 多 renderer 验证（部分失败）

**触发时间**：2026-05-09
**任务**：深挖 CARLA 替代品 + 多 renderer 对照实验先例

| Agent | 任务 | 状态 |
|---|---|---|
| #12 | CARLA 替代方案深挖（MetaDrive/Scenic/Waymax） | **配额限制失败**（rate limit reset 22:10 Asia/Shanghai） |
| #13 | 多渲染器对比的可行性 | **配额限制失败** |

**应对**：基于前面 11 个 agent 已有材料 + 公开知识自行综合判断：
- MetaDrive 不原生支持 OSC 2.0，Bench2Drive 用不上 → 不替代 CARLA
- Scenic 3.x 是 DSL 层，仍要选 CARLA / MetaDrive 后端 → 可作 Phase 3 升级
- Waymax 许可不稳（早期非商用）→ 弃
- ScenarioRunner 强依赖 carla.* 模块 → 不能 standalone
- 多 renderer 对照在 2026 公开研究空白 → 落地了就是 paper 角度

**v4 架构未变**，继续推进到 sanity check。

---

### 第 6 轮：落地 sanity check → v4→v4-final

**触发时间**：2026-05-09 晚
**目标**：动手前确保所有 v4 组件真实可访问

| Agent | 任务 | 关键发现 |
|---|---|---|
| #14 | v4 组件落地真实性核查 | **0 个 RED**；2 个 YELLOW：CARLA 0.10 是 17 月无 patch 的 dead branch（0.9.16 才是主线）；Senna 论文只 nuScenes 报点，无 NAVSIM v2 数字（需自建 harness）；OSC 2.0 actor flow 可能是 stub |
| #15 | 数据集与评测库可获取性 | **1 个硬冲突**：**Bench2Drive 仍锁 CARLA 0.9.15**，与 v4 写 0.10 直接冲突；NAVSIM v2 metric 不能裸 import EPDMS（需 Scene pickle adapter ~1 周）；HUGSIM GREEN；DAIR-V2X-V GREEN（22k 帧 + Google Drive example）；ONCE 申请页 1 年未更新静默风险；DrivingDojo 实际 283GB 不是 PB |

**v4→v4-final 触发**：
- CARLA 0.10 不能作主线 → 改 0.9.16 (UE4) 主 + 0.10 副双轨
- 数据策略改：nuScenes mini + DrivingDojo HF + ApolloScape 北京（免审批）作 MVP；ONCE / DAIR-V2X 全集并行申请不阻塞
- NAVSIM Scene pickle adapter ~1 周计入 D7

**v4-final 架构**：见 `docs/architecture.md`

---

## 4. 架构演化时间线

| 版本 | 时间 | 主骨架 | 渲染 | 触发反转 |
|---|---|---|---|---|
| **v1** | 2026-05-08 上午 | AlpaSim + SimScale | NuRec | 第 1 轮初始判断 |
| **v2** | 2026-05-08 下午 | WorldEngine + AlpaSim | DriveStudio + gsplat | 第 2 轮：NuRec 闭源、AlpaSim 文档缺失 |
| **v3** | 2026-05-08 傍晚 | CARLA headless | gsplat 主 + Cosmos 副 | 第 3 轮：WorldEngine 是 vapor |
| **v4** | 2026-05-09 | CARLA + NAVSIM v2 + 三 renderer | Cosmos 主 + gsplat 副 + CARLA UE | 第 4 轮：用户加"离线批跑"约束；NAVSIM v2 是事实标准 |
| **v4-final** | 2026-05-09 晚 | **CARLA 0.9.16+0.10 双轨 + NAVSIM v2 metric + 四 renderer** | **A1+A2+B+C** | 第 6 轮 sanity：CARLA 0.10 死分支；自研非商用约束放松；nuScenes mini 作 MVP |

---

## 5. 关键决策回顾（D1–D8）

### D1 闭环骨架：CARLA 0.9.16 主 + 0.10 副

- **v1**: AlpaSim → 闭源接入未文档
- **v2**: WorldEngine → 4s pseudo-loop demo
- **v3**: CARLA headless → 单一版本
- **v4**: CARLA 0.10 (UE5) → dead branch
- **v4-final**: CARLA 0.9.16 (UE4) 主 + 0.10 (UE5) 副双轨 ✓

**Why**：0.9.16 是官方维护主线 + Bench2Drive 锁 0.9.15 兼容；0.10 视觉升级实验保留作 A2 满足"UE5+UE4 都做"

### D2 MVP E2E 算法：SparseDriveV2 主 + Senna 副

- **v1–v3**: SparseDrive (V1)
- **v4**: Senna (开源 VLA) 主
- **v4-final**: SparseDriveV2 主（NAVSIMv2 90.38 EPDMS, GREEN）+ Senna 副（YELLOW，需自建 harness）

**Why**：SparseDriveV2 数字现成、可立即作 baseline；Senna VLA 优势在不要求实时时显现，作副线增强差异化

### D3 首个数据：nuScenes mini + 中国数据并行

- **v1**: ONCE 多城环视
- **v2–v3**: ONCE 单段
- **v4**: ONCE 单段
- **v4-final**: **nuScenes mini（免审批 MVP）+ ApolloScape 北京 + DrivingDojo HF**；ONCE / DAIR-V2X 并行申请不阻塞

**Why**：用户明确"避免数据申请不通过的风险"；ONCE 申请页 1 年未更新静默风险

### D4 渲染层：四轨道并列

- **v1**: NuRec → 闭源
- **v2**: DriveStudio + gsplat
- **v3**: gsplat 主 + Cosmos 副 + CARLA UE5 备用
- **v4**: 三 renderer 对照（CARLA UE + Cosmos + gsplat）
- **v4-final**: 四 renderer（A1=UE4 / A2=UE5 / B=Cosmos / C=gsplat）

**Why**：用户"UE5+UE4 都做"+ "三 renderer 对照"双重要求

### D5 Case 编辑：OSC 2.0 + ScenarioRunner

- **v1–v2**: 不明确
- **v3+**: OSC 2.0 + ScenarioRunner ✓

**Why**：OSC 2.0 是社区标准；CARLA 是唯一支持开源仿真；Bench2Drive 220 case 免费继承

### D6 渲染路由：Renderer Python ABC（v4 起删除 gRPC）

- **v3**: gRPC fork NuRec protobuf
- **v4+**: 删除 gRPC，Python ABC 直接 import

**Why**：用户"离线批跑"约束让 IPC 复杂度归零

### D7 评测脚手架：NAVSIM v2 metric + Scene pickle adapter + HUGSIM

- **v1–v3**: HUGSIM 主
- **v4**: NAVSIM v2 主 + HUGSIM 副
- **v4-final**: 同 v4，但加 Scene pickle adapter ~1 周

**Why**：NAVSIM v2 metric 不能裸 import EPDMS（sanity check 发现）

### D8 阶段策略：Phase 1 单轨 → Phase 2 四轨 → Phase 3 真闭环

- **v4-final**: Phase 1 A1 + nuScenes mini + SparseDriveV2 → 第一份 EPDMS 报告
- Phase 2: 四轨对照 + ApolloScape + DrivingDojo LoRA + Senna
- Phase 3: HUGSIM 真闭环 + ONCE 中国 case + ReconDreamer++

---

## 6. 已退出方案及具体退出原因

| 方案 | 退出版本 | 退出原因（具体证据） |
|---|---|---|
| **NuRec 容器** | v2 | 训练管线 + Fixer + 推理服务全闭源 docker `nvcr.io/nvidia/nre/nre-ga`；论坛报 "Payment Required" 错误（forum 365098）；918 预训练资产 NVIDIA AV License 12 月期限 + 不可再分发；CARLA tutorial 当前 broken（CARLA #9667） |
| **AlpaSim 作主线** | v3 | 默认 renderer 仅 NuRec（闭源）；第三方 planner（UniAD/SparseDrive）接入官方未文档（DESIGN.md）；外部独立复现报告 0 条 |
| **WorldEngine** | v3 | 实际是 NAVSIM v2 后训练 demo（仅 4s pseudo-closed-loop）；硬绑 nuPlan（MTGS 校准 + scenario schema + PDM 评测全为 nuPlan 量身）；arXiv 截至 2026-05-09 未发布；建仓 2026-04-10 仅 15 commits + 1 个未解 8-GPU bug；改造中国数据 ≥2 个月 |
| **SimScale 作 agent 框架** | v2 | 误读，实际是 sim-real 训练辅助框架（CVPR'26 Oral 论文路线），不是 agent / 仿真器 |
| **DriveArena** | v3 | 2024-11 起半停滞（最后 commit 2024-11） |
| **纯生成式无显式 3D（Panacea / Drive-WM / DrivingDiffusion）** | v1 | off-trajectory 几何漂移 |
| **GAIA-2 / GAIA-3** | v1 | 闭源 |
| **LGSVL** | v1 | 2022 已停服 |
| **AirSim** | v1 | 已停更 |
| **商业街景（百度/高德/腾讯）** | v1 | ToS 不允许爬取再训练；自研也按这个边界（避免 sim2world 落地阶段卡住） |
| **nuScenes-CN / OpenLane-V2 中国** | v2 | 不存在 |
| **DAIR-V2X 作重建主源** | v2 | 路端固定相机 + 非 ego-centric；V 子集 22k 帧可作辅助 / hello-world |
| **自研 case DSL** | v3 | 追平 OpenDRIVE + behavior tree + ScenarioRunner 生态需 6–12 人月 |
| **MetaDrive 替代 CARLA** | v4 | 不原生支持 OSC 2.0；Bench2Drive 220 case 用不上；既然 CARLA 必装（UE 渲染要保留），无意义 |
| **Scenic / Waymax 替代 CARLA** | v4 | Scenic 是 DSL 层不是 runtime；Waymax 许可早期非商用 |
| **ScenarioRunner standalone** | v4 | OSC 2.0 解析强依赖 `carla.*` 模块，不能 standalone |
| **3DGRUT (nv-tlabs) 作主渲染** | v3 | 仅 OptiX 反射时启用，gsplat 3DGUT 模式已覆盖 90% 能力 |
| **CARLA UE5 (0.10) 作生产主线** | v4-final | **17 个月无 patch（2024-12 之后）；ScenarioRunner 0.9.16 无 0.10 兼容声明；Bench2Drive 锁 0.9.15** |

---

## 7. 最终架构 v4-final（速查）

```
OSC 2.0 case → CARLA 0.9.16 synchronous (--RenderOffScreen)
                  ↓ {HDMap, ego, agents, weather, t}
   ┌──────────────┼──────────────┬──────────────┐
   ▼              ▼              ▼              ▼
CARLA UE4    CARLA UE5      Cosmos+LoRA   gsplat 重建
(主 baseline)(实验视觉)     (生成中国感)  (sim2real)
   └──────────────┴──────────────┴──────────────┘
                  ↓ RGB 6/8 cam
                  ▼
            E2E 算法（SparseDriveV2 主 + Senna 副）
                  ↓ trajectory K×3
                  ▼
            自行车模型 + Pure Pursuit
                  ↓
            CARLA apply_control() 闭环
                  ↓
            EPDMS 报告（× 4 轨 × N 算法）
```

详见 [`docs/architecture.md`](architecture.md)。

---

## 8. 调研过程的经验教训

### 8.1 有效的模式

1. **并行多 agent + 自包含 prompt**：每轮 2–4 个 agent 并行，单 prompt 自带项目背景（不依赖之前对话），背景研究效率最高
2. **强制评级（GREEN/YELLOW/RED）**：迫使 agent 落到具体证据，避免"应该可以"的乐观估计
3. **"信息缺口"明确标注**：当 agent 搜不到某个数据点，明确说"未发现"比瞎猜值钱 100 倍
4. **死胡同保留退出原因**：避免几小时后又"是不是该回头看 NuRec"
5. **每轮调研后立即更新 architecture.md / memory**：知识沉淀为代码可执行的形式
6. **Sanity check 在动手前**：6 个 v4 组件 + 10 个数据/库逐个验证，提前暴露所有 YELLOW

### 8.2 踩过的坑

1. **过度信任"开源声明"**：AlpaSim / WorldEngine / NuRec 都自称开源，实际：
   - NuRec：仅算法核 (3DGRUT) 开源，训练管线和推理服务全闭源 docker
   - AlpaSim：代码 Apache 但默认 renderer 是 NuRec，第三方 planner 接入未文档
   - WorldEngine：开源但是 4s pseudo-loop demo + 硬绑 nuPlan + arXiv 未发
2. **过度信任"GitHub stars"**：DriveArena 449★ 但 2024-11 起半停滞
3. **第一轮 agent 报告里把 SimScale 当 agent 框架**：实际是 sim-real 训练辅助
4. **没有提前问"是否要求实时"**：直到第 4 轮用户加"离线批跑"约束才反转 v3→v4，浪费 1 轮迭代设计 gRPC
5. **没有提前问"商用约束"**：到 v4-final 才发现"自研非商用"让 CC-BY-NC / OML 担忧全部归零

### 8.3 应该提前问的问题（写给未来自己）

- **是否要求实时？**（影响渲染、E2E 算法、IPC 设计）
- **商用还是自研？**（影响许可证、出口管制、数据策略）
- **数据是否必须中国？**（不是中国可以接受 nuScenes/Waymo，加 nuScenes mini 作 MVP）
- **闭环深度需要多深？**（4s pseudo-loop / 30s synchronous 慢跑 / 真实时）
- **是否需要可视化对外汇报？**（影响是否上 Cosmos 高质量视频路线）

---

## 9. 调研产出物清单

### 文档（已落地）
- `README.md` — 项目入口
- `docs/architecture.md` — v4-final 架构（8 决策 / 模块 / 数据流 / 风险表 / 死胡同 / 阶段计划）
- `docs/week1_plan.md` — Phase 1 W1 详细任务（Day 0 + 5 hello-world）
- `docs/research_journey.md` — 本文档（调研历程）
- `requirements.txt` — 依赖清单 v4-final
- `src/autosim/e2e_plugins/protocol.py` — E2E 算法 Plugin Protocol（renderer-agnostic，从 v1 至 v4-final 未改）

### 记忆（持久化）
- `~/.claude/projects/E--test-AutoSim/memory/MEMORY.md` — 主索引
- `memory/project_autosim.md` — 项目目标
- `memory/user_role.md` — 用户角色
- `memory/project_constraints.md` — 算力 / 数据 / 商业边界（含自研非商用注脚）
- `memory/project_tech_stack.md` — v4-final 技术栈完整决策表

### Agent 报告原始资料
位置：`C:\Users\elane\AppData\Local\Temp\claude\E--test-AutoSim\db396173-c3c7-4b90-ade9-db8421856acc\tasks\`

| Agent ID | 任务 | 轮次 |
|---|---|---|
| ae9ba423d2f55fd05 | E2E 算法接口 | 第 1 轮 |
| a85065470d4f73add | 生成式世界模型 | 第 1 轮 |
| a68ebd4c71bb55cc9 | 3DGS/NeRF 闭环重建 | 第 1 轮 |
| adcabe3977aadc5db | 数据集与现有仿真器 | 第 1 轮 |
| a02f1f1d27b39bc3f | NuRec 深挖 | 第 2 轮 |
| aafaedfb1cd806592 | AlpaSim 深挖 | 第 2 轮 |
| af052d04dcdd44656 | WorldEngine 深挖 | 第 3 轮 |
| a472234cdde061790 | 开源 GS 渲染栈 | 第 3 轮 |
| a4dbc3452356dc43e | CARLA case 编辑角色 | 第 3 轮 |
| a04a4ea8c8d576428 | Cosmos 主渲染可行性 | 第 4 轮 |
| abc471109d8f0c92d | 离线批跑评测 + VLM E2E | 第 4 轮 |
| a675004584742200b | CARLA 替代方案（FAILED） | 第 5 轮 |
| a8fa474f53df407cf | 多渲染器对比（FAILED） | 第 5 轮 |
| a932d6016b23e81d4 | v4 组件 sanity | 第 6 轮 |
| aa6ead8d6db7c72b5 | v4 数据集 sanity | 第 6 轮 |

---

## 10. 启动 Phase 1 的前置条件 checklist

- [x] v4-final 方向锁定
- [x] 0 个 RED 阻断已确认
- [x] 2 个 YELLOW 已识别 + 缓解（CARLA 0.10 dead branch / Senna NAVSIM v2 harness）
- [x] 数据策略避审批（nuScenes mini + DAIR-V2X-V example + ApolloScape + DrivingDojo HF）
- [x] 自研非商用约束确认，CC-BY-NC / OML 不阻塞
- [x] 所有文档 + 记忆已更新到 v4-final
- [ ] **用户说"启动 Phase 1 D0"**

启动后第 1 周：
1. **Day 0**：发 ONCE / DAIR-V2X 申请邮件 + 下载 nuScenes mini + DAIR-V2X-V example + ApolloScape 北京段
2. **Day 1**：项目骨架 + CARLA 0.9.16 / 0.10 双 hello-world
3. **Day 2**：ScenarioRunner OSC 2.0 + Bench2Drive 兼容性
4. **Day 3**：gsplat 3DGUT + DriveStudio 单段重建
5. **Day 4**：Cosmos HF 下载 + Senna standalone
6. **Day 5**：SparseDriveV2 + Plugin Protocol + NAVSIM Scene pickle adapter

详见 [`docs/week1_plan.md`](week1_plan.md)。
