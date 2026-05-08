# AutoSim

纯视觉端到端自动驾驶闭环仿真器。中国城市，运动学车辆，sim2real 落地。

## 状态

阶段 2（架构 PoC，方向已锁定 v3）— 2026-05-08。仓库刚启动，尚无可运行代码。

## 七个已锁定决策

| # | 决策 | 选定 |
|---|---|---|
| D1 | 闭环骨架 | CARLA 0.10/0.9.16（headless 逻辑层，UE 渲染关闭） |
| D2 | MVP 算法 | SparseDrive |
| D3 | 首个数据 | ONCE 单段；ApolloScape 兜底 |
| D4 | 渲染层 | gsplat 1.5 (3DGUT) 推理 + DriveStudio + OmniRe 训练 |
| D5 | Case 编辑 | OpenSCENARIO 2.0 + ScenarioRunner（继承 Bench2Drive 220 条 + 自写中国 case） |
| D6 | 渲染路由 | fork NuRec gRPC protobuf，backend 换 gsplat |
| D7 | 评测脚手架 | HUGSIM（70 序列 + extrapolated KID benchmark） |

## 核心架构（v3）

```
CARLA (case + 物理 + 闭环)        ←  OpenSCENARIO 2.0 + ScenarioRunner
   │  gRPC  (camera_pose, actor_poses, t)
   ▼
gsplat 1.5 (3DGUT) Renderer Service
   ↑
   │  训练产物 .pt
   │
DriveStudio + OmniRe (训练)       ←  ONCE / ApolloScape / DrivingDojo
   │  RGB (6/8 cam)
   ▼
E2E 算法插件 (SparseDrive)         ←  src/autosim/e2e_plugins/protocol.py
   │  trajectory (K×3)
   ▼
自行车模型 + Pure Pursuit
   │
   └─→ CARLA apply_control() 闭环
```

## 已退出主线（不要再考虑）

- **NuRec 容器**：训练管线 + 推理服务全闭源 docker，预训练资产全欧美且不可再分发
- **AlpaSim**：默认 renderer 仅 NuRec；第三方 planner 接入未文档；外部独立复现 0
- **WorldEngine**：实际是 4 秒 NAVSIM v2 pseudo-closed-loop demo，硬绑 nuPlan，arXiv 未发
- **DAIR-V2X 作重建主源**：路端固定相机非 ego-centric，仅作 V2X 评测专用
- **GAIA-2/3 / 商业街景 / LGSVL / AirSim**：闭源 / ToS 禁止 / 已停服

## 文档

- [架构 v3](docs/architecture.md)
- [Week 1 任务](docs/week1_plan.md)

## 决策演化

| 版本 | 闭环骨架 | 渲染 | 备注 |
|---|---|---|---|
| v1 | AlpaSim 主 + SimScale 补 | NuRec | SimScale 误读为 agent 框架 |
| v2 | WorldEngine 主 + AlpaSim 副 | DriveStudio + gsplat | NuRec 闭源被发现 |
| **v3** | **CARLA（headless）** | **gsplat 1.5 + DriveStudio + OmniRe** | WorldEngine 是 vapor，CARLA gRPC 路由先例 |
