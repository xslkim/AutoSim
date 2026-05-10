# AutoSim

纯视觉端到端自动驾驶**离线批跑**仿真器。中国城市，运动学车辆，sim2real 落地。**自研、非商用。**

## 状态

阶段 2（架构 PoC，方向最终锁定 v4-final）— 2026-05-09。仓库刚启动，尚无可运行代码。

## 八个已锁定决策

| # | 决策 | 选定 | 评级 |
|---|---|---|---|
| D1 | 闭环骨架 | CARLA 0.9.16 (UE4) 主 + CARLA 0.10 (UE5) 副双轨 | 🟡 |
| D2 | MVP E2E 算法 | SparseDriveV2 主 + Senna 副；横评 Hydra-NeXt / DiffusionDrive / DriveLM / OpenEMMA | 🟢/🟡 |
| D3 | 首个数据 | nuScenes mini (免审批 MVP) + ApolloScape 北京 + DrivingDojo HF；ONCE / DAIR-V2X 并行申请不阻塞 | 🟢 |
| D4 | 渲染层（四轨道并列） | A1=CARLA UE4 / A2=CARLA UE5 / B=Cosmos 双 backend (B-cn=Predict2.5+LoRA + B-av=Drive-Dreams；串行) / C=gsplat+DriveStudio | 🟢 |
| D5 | Case 编辑 | OpenSCENARIO 2.0 + ScenarioRunner；actor flow 可能是 stub，复杂场景退 Python API | 🟡 |
| D6 | 渲染路由 | Renderer Python ABC（无 gRPC，离线让 IPC 复杂度归零） | 🟢 |
| D7 | 评测脚手架 | NAVSIM v2 metric 库 + 自建 Scene pickle adapter（~1 周）；HUGSIM 副线 Phase 3 接入 | 🟡 |
| D8 | 阶段策略 | Phase 1 A1 单轨 → Phase 2 四轨对照 → Phase 3 HUGSIM + 中国 case | 🟢 |

## 核心架构（v4-final）

```
OSC 2.0 case → CARLA 0.9.16 synchronous (--RenderOffScreen)
                  ↓ {HDMap, ego, agents, weather, t}
   ┌──────────────┼──────────────┬──────────────┐
   ▼              ▼              ▼              ▼
CARLA UE4     CARLA UE5      Cosmos+LoRA    gsplat 重建
(主 baseline) (实验视觉)     (生成中国感)   (sim2real 真照片)
   └──────────────┴──────────────┴──────────────┘
                  ↓ RGB 6/8 cam
                  ▼
            E2E 算法 (Plugin Protocol)
            SparseDriveV2 / Senna / ...
                  ↓ trajectory K×3
                  ▼
            自行车模型 + Pure Pursuit
                  ↓
            CARLA apply_control() 闭环
                  ↓
            EPDMS 报告（× 4 轨 × N 算法）
```

## 第一个里程碑（单轨闭环）

CARLA 0.9.16 (UE4) + nuScenes mini + SparseDriveV2，按"场景定义 → 仿真核心 → 图像渲染 → 端到端算法 → 控制闭环 → 评测报告"六阶段打通。

不在本里程碑：CARLA UE5 / Cosmos / Senna / gsplat / DAIR-V2X / ApolloScape / DrivingDojo / Bench2Drive 全套兼容。详见 [docs/milestone_1_plan.md](docs/milestone_1_plan.md)。

## 已退出主线（不要再考虑）

NuRec 容器 / AlpaSim 作主线 / WorldEngine / SimScale 作 agent / DriveArena / GAIA-2/3 / 商业街景 / LGSVL / AirSim / DAIR-V2X 作重建主源 / 自研 case DSL / MetaDrive / Scenic / Waymax 替代 CARLA。详见 [docs/architecture.md](docs/architecture.md) 第 7 节。

## 文档

- [高层立项简报](docs/executive_brief.md)
- [架构 v4-final](docs/architecture.md)
- [Milestone 1 计划](docs/milestone_1_plan.md) — 第一个里程碑：单轨闭环打通（按任务组织）
- [调研历程与方案演化](docs/research_journey.md) — 6 轮调研 / 15 个 agent 报告 / 4 轮架构反转的完整记录
- ~~[Week 1 任务 v4-final](docs/week1_plan.md)~~ — 已废弃，由 Milestone 1 计划替代

## 决策演化

| 版本 | 主骨架 | 渲染 | 触发反转 |
|---|---|---|---|
| v1 | AlpaSim 主 + SimScale 补 | NuRec | SimScale 误读；NuRec 闭源 |
| v2 | WorldEngine 主 + AlpaSim 副 | DriveStudio + gsplat | NuRec/AlpaSim 接入门槛暴露 |
| v3 | CARLA headless | gsplat 主 + Cosmos 副 | WorldEngine 是 vapor |
| v4 | CARLA + NAVSIM v2 + 三 renderer | Cosmos 主 + gsplat 副 + CARLA UE | 离线约束 + 三轨道对照 |
| **v4-final** | **CARLA 0.9.16+0.10 双轨 + NAVSIM v2 metric + 四 renderer** | **A1+A2+B+C** | **sanity 后 CARLA 0.10 死分支风险 + 自研非商用约束放松 + nuScenes mini 作 MVP 首数据避审批** |
