# AutoSim 架构 v0.1

> 2026-05-08，基于 4 份并行 SOTA 调研的交叉印证结果。

## 0. 决策摘要

| # | 决策 | 选项 | Why |
|---|---|---|---|
| D1 | 闭环骨架 | **AlpaSim 主 + SimScale 反应式 agent 补** | 工业级骨架 + 中国友好的反应式神经渲染（CVPR'26 Oral），兼顾生态与本地化 |
| D2 | MVP E2E 算法 | **SparseDrive** | 9 FPS、稀疏 query 不依赖 BEV、Bench2Drive 44 DS、对中国数据迁移友好 |
| D3 | 首个数据 | **DAIR-V2X 北京路口** | 数据量小、V2X 已多视角校准、ego 轨迹完整、单路口闭环最易跑通 |

## 1. 整体架构

```
┌─────────────────────── 闭环骨架 (AlpaSim) ──────────────────────────┐
│  Scenario Manager  │  Ego State  │  Reactive Agents (SimScale 风格)  │
└──────────┬──────────────────────────────────────┬──────────────────┘
           │                                      │
  ┌────────▼──────────┐              ┌───────────▼──────────┐
  │  几何/渲染层        │              │  E2E 算法插件         │
  │  ┌──────────────┐ │  Image       │  统一接口:            │
  │  │ NuRec/3DGUT  │ ├─────────────▶│  obs={imgs,ego,nav}  │
  │  │ DriveStudio  │ │              │  →act={traj K×3}     │
  │  └──────┬───────┘ │              │                       │
  │         │         │  Trajectory  │  Hydra-NeXt / VAD /  │
  │  ┌──────▼───────┐ │◀─────────────│  UniAD / SparseDrive │
  │  │ Off-traj 修复 │ │              │  / DiffusionDrive    │
  │  │ ReconDreamer │ │              └───────────┬──────────┘
  │  │ + DriveX     │ │                          │
  │  └──────────────┘ │              ┌───────────▼──────────┐
  └────────┬──────────┘              │  运动学跟踪器          │
           │                         │  自行车模型 +          │
           │  Layout/Edit            │  Pure Pursuit / LQR   │
  ┌────────▼──────────┐              └───────────┬──────────┘
  │  世界模型层         │                         │
  │  Cosmos-Predict2.5│◀──────── 训练 cousin 轨迹 ┘
  │  + Vista (备份)   │
  └────────┬──────────┘
           │  生成补全
           │
  ┌────────▼─────────────────────────────────────────────────┐
  │  数据层（中国城市）                                        │
  │  重建主体: DAIR-V2X (MVP) → ONCE + ApolloScape           │
  │  风格补充: SODA10M                                       │
  │  世界模型 FT: DrivingDojo (900k clips)                    │
  └──────────────────────────────────────────────────────────┘
```

## 2. 目录结构

```
AutoSim/
├── README.md
├── requirements.txt
├── docs/
│   ├── architecture.md          # 本文
│   └── week1_plan.md
├── src/
│   └── autosim/
│       ├── core/                # AlpaSim 封装；ScenarioRunner、tick 循环
│       ├── renderer/            # NuRec / DriveStudio 适配
│       ├── world_model/         # Cosmos-Predict2.5 推理 wrapper
│       ├── offtraj/             # ReconDreamer++ / DriveX 修复
│       ├── kinematics/          # 自行车模型、Pure Pursuit、LQR
│       ├── agents/              # 反应式 agent（SimScale 风格）
│       ├── scenarios/           # YAML/Python case DSL 加载
│       ├── e2e_plugins/         # 统一插件协议 + 各算法 adapter
│       │   ├── protocol.py      # ★ 已落地，见仓库
│       │   ├── sparsedrive.py
│       │   ├── uniad.py
│       │   └── ...
│       ├── data_adapters/       # 数据集 → 内部统一格式
│       │   ├── dair_v2x.py
│       │   ├── once.py
│       │   └── apolloscape.py
│       └── eval/                # NAVSIM/Bench2Drive/HUGSIM/DriveArena 钩子
├── scripts/
│   ├── reconstruct_scene.py     # 数据 → 3DGS 资产
│   ├── run_closed_loop.py
│   └── benchmark_e2e.py
├── scenarios/
│   └── examples/
│       └── dair_v2x_intersection_001.yaml
├── tests/
└── third_party/                 # git submodule
    ├── alpasim/
    ├── drivestudio/
    ├── sparsedrive/
    ├── recondreamer/
    └── cosmos-predict2.5/
```

## 3. 关键接口

### 3.1 E2E 算法插件（已落地）

见 [`src/autosim/e2e_plugins/protocol.py`](../src/autosim/e2e_plugins/protocol.py)。

仿真器只消费 `Action.trajectory`（K×3，ego 系），由 `kinematics/` 模块的 Pure Pursuit 跟踪器驱动车辆——这是支持算法插拔的关键解耦点。Tesla 风格直接控制方案走 `Action.control` 通道（可选）。

### 3.2 场景 YAML schema（Week 2 落地）

```yaml
scenario_id: dair_v2x_intersection_001
data_source:
  dataset: DAIR-V2X
  split: SPD
  sequence_id: ...
ego:
  init_pose: {x, y, heading}
  route: [{x, y}, ...]
weather: clear        # clear|rain|fog|night
agents:
  - id: vehicle_001
    type: reactive    # reactive|replay|scripted
    init_pose: ...
edits:                # 可选 case 编辑
  - {op: insert_pedestrian, at: {x, y}, time: 3.0}
  - {op: weather_change, to: rain, time: 10.0}
evaluation:
  metrics: [PDMS, success_rate, comfort, off_traj_KID]
  horizon_s: 30
```

## 4. 数据流（单 tick）

```
t=k:
  scenario.update(t)              # case DSL 触发的编辑生效
  agents.step(t)                  # 反应式 agent 状态更新
  obs = renderer.render(ego, agents, scene_3dgs, world_model_inpaint?)
  action = planner.step(obs)      # E2E 算法
  ego = kinematics.advance(ego, action.trajectory, dt)
  eval.log(t, ego, action, ground_truth?)
t=k+1
```

## 5. 已识别风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|---|
| R1 | NuRec 无中国预训练资产，必须自重建 | 高 | 高 | 用 DAIR-V2X 单路口先跑通管线，再扩 ONCE |
| R2 | AlpaSim 开源完整度不足 / 文档缺失 | 中 | 高 | 备选 OpenDriveLab WorldEngine+SimScale |
| R3 | Cosmos OML 在国内商业落地合规未明 | 中 | 中 | MVP 用 Cosmos 做研究；落地版替换为 Vista（Apache 2） |
| R4 | ReconDreamer++ 训练算力开销大 | 中 | 中 | 阶段 5 才接入；先用 DriveStudio 重建插值视角 |
| R5 | DAIR-V2X 数据获取需邮件审批 | 中 | 低 | 兜底用 ApolloScape 已公开部分 |
| R6 | SparseDrive 在中国数据上未公开评测 | 中 | 低 | 先用 nuScenes 权重做迁移推理；必要时在 DAIR-V2X 上 FT |

## 6. 评测指标（多 benchmark 联评）

| Benchmark | 协议 | 关键指标 | 用途 |
|---|---|---|---|
| Bench2Drive | CARLA 闭环 | DS（Driving Score） | 算法绝对能力上限 |
| NAVSIM v2 | 伪闭环（重放） | PDMS | 与社区可比 |
| DriveArena | HDMap 闭环 | 成功率 | 中国 HDMap 编辑闭环 |
| HUGSIM | extrapolated NVS | KID, FID | off-trajectory 渲染质量（独立于算法） |
| 自定义 | 中国路口（DAIR-V2X 重建） | 闭环成功率 + 舒适度 | sim2real 自评 |

## 7. 死胡同（已排除，不再考虑）

- 纯生成式无显式 3D（Panacea / Drive-WM / DrivingDiffusion）：off-traj 几何漂移
- GAIA-2/3：闭源
- LGSVL：2022 已停服
- AirSim：已停更
- 商业街景（百度/高德/腾讯）：ToS 禁止商业重训
- nuScenes-CN（不存在）/ OpenLane-V2 中国部分（不存在）

## 8. 后续阶段

- 阶段 3（4–6 周）：单场景闭环 MVP — DAIR-V2X 单路口 → DriveStudio 重建 → AlpaSim 闭环 → SparseDrive 接入
- 阶段 4（4 周）：算法接口标准化 + Case DSL
- 阶段 5（4–6 周）：Off-traj 修复 + 多算法对比 + sim2real KPI
