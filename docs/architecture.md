# AutoSim 架构 v3

> 2026-05-08，方向锁定。基于 7 个并行 SOTA 调研的交叉印证 + 2 轮架构反转结果。

## 0. 决策摘要

| # | 决策 | 选定 | Why |
|---|---|---|---|
| D1 | 闭环骨架 | **CARLA 0.10/0.9.16（headless 逻辑层）** | 唯一支持 OSC 1.x+2.0 的开源仿真；真长闭环；Bench2Drive 220 条 case 现成；NuRec gRPC 已铺好"逻辑/渲染解耦"先例 |
| D2 | MVP E2E 算法 | **SparseDrive** | 9 FPS、稀疏 query、不依赖 BEV、Bench2Drive 44 DS、对中国数据迁移友好 |
| D3 | 首个数据 | **ONCE 单段**；ApolloScape 兜底 | 7 相机环视 + 40 线 LiDAR 结构最接近 Waymo；DriveStudio adapter ~1 周 |
| D4 | 渲染层 | **gsplat 1.5 (3DGUT) 推理 + DriveStudio + OmniRe 训练** | NuRec 同算法核但完全 Apache + MIT；H100 ~80 FPS @ 6×720p |
| D5 | Case 编辑 | **OpenSCENARIO 2.0 + ScenarioRunner** | actor-flow 写中国 case 复用率 ~60%，比 1.x 简洁 3 倍；vs 自研 DSL 节省 6–9 人月 |
| D6 | 渲染路由 | **fork NuRec gRPC protobuf，backend 换 gsplat** | 官方铺好的 IPC，protobuf 定义在 docs.nvidia.com/nurec/api/grpc_api_guide.html |
| D7 | 评测脚手架 | **HUGSIM** 70 序列 benchmark | 唯一覆盖 extrapolated KID（off-trajectory NVS 质量评测） |

## 1. 整体架构

```
┌─── CARLA 0.10 / 0.9.16 (case + 物理 + 闭环) ────────────────┐
│  --RenderOffScreen + no_rendering_mode                       │
│  • OpenSCENARIO 2.0 + ScenarioRunner                          │
│  • Traffic Manager + behavior tree + PhysX                    │
│  • OpenDRIVE HDMap                                            │
│  • 50–100 Hz state output                                    │
│  • Bench2Drive 220 条 case + 自写中国 case (~3 人月)          │
└─────────────────┬─────────────────────────────────────────────┘
                  │ gRPC (fork NuRec protobuf)
                  │ {camera_pose, actor_poses, timestamp}
                  ▼
┌─── 自建 Renderer Service ─────────────────────────────────────┐
│  gsplat 1.5 (3DGUT 模式)  [Apache, 5k★]                       │
│    • rasterization(with_ut=True, with_eval3d=True,            │
│        viewmats_rs=...)                                        │
│    • 原生 fisheye / RS / 多相机 batch                          │
│    • H100 ~80 FPS @ 6×1280×720                                 │
│    • 胶水代码 ~300–500 行                                      │
│        ↑                                                       │
│        │ 训练产物 .pt                                          │
│  DriveStudio + OmniRe  [MIT, 1.2k★]                           │
│    • 6 数据集 dataloader + adapter 模式                        │
│    • 静/动解耦（Static + SMPL + Deformable 行人/骑手）        │
│    • 中国数据 adapter ~600 行/数据集                           │
└─────────────────┬─────────────────────────────────────────────┘
                  │ RGB (6/8 cam)
                  ▼
┌─── E2E 算法插件 ──────────────────────────────────────────────┐
│  SparseDrive (MVP) → Hydra-NeXt / DiffusionDrive / UniAD      │
│  统一 Plugin Protocol（src/autosim/e2e_plugins/protocol.py）  │
└─────────────────┬─────────────────────────────────────────────┘
                  │ trajectory (K×3)
                  ▼
            自行车模型 + Pure Pursuit / LQR
                  │
                  └─→ CARLA apply_control()  闭环回灌

┌─── 评测脚手架（独立路径） ───────────────────────────────────┐
│  HUGSIM [MIT]  70 序列 + extrapolated KID benchmark          │
│  把 closed_loop.py 里 gaussian_renderer 换成我们的 service    │
└────────────────────────────────────────────────────────────┘

┌─── 可选 alternative renderer ────────────────────────────────┐
│  Cosmos-Predict2.5 (Apache+OML) 或 Vista (Apache)            │
│  CARLA → HDMap+box+ego 条件 → 直接生成图像                    │
└────────────────────────────────────────────────────────────┘
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
│       ├── core/                # 闭环 driver；CARLA client wrapper、tick 循环
│       ├── bridges/             # ★ v3 新增：CARLA ↔ Renderer gRPC bridge (fork NuRec proto)
│       ├── renderer/            # gsplat 3DGUT renderer service
│       ├── training/            # DriveStudio + OmniRe 训练入口（薄封装）
│       ├── world_model/         # 可选：Cosmos / Vista 推理（alternative renderer）
│       ├── kinematics/          # 自行车模型、Pure Pursuit、LQR
│       ├── scenarios/           # OSC 2.0 case 加载 + 中国 case 库
│       ├── e2e_plugins/         # 统一插件协议 + 各算法 adapter
│       │   ├── protocol.py      # ★ 已落地，见仓库
│       │   ├── sparsedrive.py
│       │   └── ...
│       ├── data_adapters/       # 数据集 → DriveStudio 内部格式
│       │   ├── once.py
│       │   ├── apolloscape.py
│       │   └── nuscenes.py
│       └── eval/                # HUGSIM / NAVSIM / Bench2Drive 评测钩子
├── scripts/
│   ├── reconstruct_scene.py     # 数据 → 3DGS 资产（DriveStudio 训练入口）
│   ├── run_closed_loop.py       # CARLA + Renderer + Plugin 闭环
│   └── benchmark_e2e.py
├── scenarios/                   # OSC 2.0 case 文件
│   ├── chinese/
│   │   ├── ev_cut_in.osc
│   │   ├── delivery_rider.osc
│   │   └── tidal_lane.osc
│   └── examples/
├── proto/                       # ★ v3 新增：gRPC proto 定义（fork NuRec）
│   └── renderer.proto
├── tests/
└── third_party/                 # git submodule
    ├── carla/                   # CARLA 仅二进制 docker，源码可不入
    ├── scenario_runner/
    ├── gsplat/                  # 实际 pip 装，submodule 仅作版本锁
    ├── drivestudio/
    ├── sparsedrive/
    └── hugsim/
```

## 3. 关键接口

### 3.1 E2E 算法插件（已落地）

见 [`src/autosim/e2e_plugins/protocol.py`](../src/autosim/e2e_plugins/protocol.py)。

仿真器只消费 `Action.trajectory`（K×3，ego 系），由 `kinematics/` 模块的 Pure Pursuit 跟踪器输出 control 调用 CARLA `apply_control()`——这是支持算法插拔的关键解耦点。Tesla 风格直接控制方案走 `Action.control` 通道（可选）。

### 3.2 Renderer gRPC bridge（v3 新增，Week 3 落地）

fork 自 NuRec gRPC：`docs.nvidia.com/nurec/api/grpc_api_guide.html`。

核心 RPC（草案）：
```protobuf
service Renderer {
  rpc Render(RenderRequest) returns (RenderResponse);
  rpc LoadScene(LoadSceneRequest) returns (LoadSceneResponse);
}
message RenderRequest {
  string scene_id = 1;
  repeated CameraPose cameras = 2;        // pose + intrinsics + distortion
  repeated ActorState actors = 3;         // 动态 agent 当前位姿（用于动态 GS 解耦）
  double timestamp = 4;
}
message RenderResponse {
  repeated bytes images = 1;              // 多相机 PNG/JPEG
  double render_ms = 2;
}
```

### 3.3 Scenario YAML / OSC 2.0 schema（Week 6+）

**case 直接写 OSC 2.0**，AutoSim 这边只需要：
- `scenarios/<case>.osc` — OpenSCENARIO 2.0 描述
- `scenarios/<case>.meta.yaml` — AutoSim 特定元数据（评测指标、horizon、ego 算法切换）

```yaml
scenario_id: chinese_ev_cut_in_001
osc_file: chinese/ev_cut_in.osc
ego:
  algorithm: sparsedrive
  init_route: [...]
weather: rain         # CARLA 原生支持
agents_override:      # 可选 OSC 之外的扩展
  reactive_traffic: true
evaluation:
  metrics: [PDMS, success_rate, comfort, off_traj_KID]
  horizon_s: 30
```

## 4. 数据流（单 tick，10 Hz）

```
t=k:
  carla.tick()                                 # CARLA 推进物理 + agent + scenario
  state = carla.get_world_snapshot()           # ego pose, actor poses, weather
  obs = renderer_client.render(                # gRPC 调 gsplat service
    scene_id, cameras=ego.cameras,
    actors=state.actors, t=k*dt
  )
  obs.merge(ego_state, nav_command, route)
  action = planner.step(obs)                   # E2E 算法
  control = pure_pursuit(action.trajectory, ego.state)
  carla.ego_vehicle.apply_control(control)     # 闭环回灌
  eval.log(t, ego, action, gt?)
t=k+1
```

## 5. 已识别风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|---|
| R1 | gsplat 3DGUT 与 DriveStudio MCMC strategy 不兼容 | 中 | 中 | 提前在 Week 1 验证；切 strategy 或 fork 后修补 |
| R2 | 中国数据 LiDAR 不密 → 几何先验差 | 中 | 高 | patch SplatAD 的 LiDAR loss 进 gsplat；ApolloScape LiDAR 较密可兜底 |
| R3 | rolling shutter 需精确 timestamp，ONCE 多相机同步可能不全 | 中 | 中 | 重新做时间对齐；Week 2 评估再决定是否启用 RS 模式 |
| R4 | CARLA gRPC 渲染路由要 fork NVIDIA proto，许可证细节 | 低 | 低 | proto 定义本身可重写（schema 不享受版权）；用作 spec 参考 |
| R5 | OSC 2.0 工具链成熟度（解析器、调试器）仍弱于 1.x | 中 | 中 | 必要时 case 库混用 1.x（ScenarioRunner 都支持） |
| R6 | ONCE 数据获取 / 许可证（学术非商用） | 低 | 中 | MVP 期没问题；商业落地阶段需评估或更换数据 |
| R7 | DriveStudio 没现成 ONCE adapter（要照 nuScenes 写 ~1 周） | 中 | 低 | 工作量已计入 Week 2 |
| R8 | Bench2Drive case 是欧美场景，不能直接当中国 case | 高 | 中 | 用作"通用驾驶能力 sanity check"；中国 case 自写 |
| R9 | CARLA UE5 渲染纯关闭运行的稳定性 | 低 | 中 | `--RenderOffScreen` + `no_rendering_mode=True` 已是官方支持模式 |
| R10 | SparseDrive 在中国数据上未公开评测 | 中 | 低 | 先用 nuScenes 权重做迁移；必要时在 ONCE 上 FT |

## 6. 评测指标（多 benchmark 联评）

| Benchmark | 协议 | 关键指标 | 用途 |
|---|---|---|---|
| Bench2Drive | CARLA 闭环（直接复用） | DS（Driving Score） | 算法绝对能力上限，免费继承 |
| NAVSIM v2 | 伪闭环（重放） | PDMS | 与社区可比 |
| HUGSIM | extrapolated NVS | KID, FID | off-trajectory 渲染质量（独立于算法） |
| 自定义 | 中国 case（OSC 2.0 + DriveStudio 重建场景） | 闭环成功率 + 舒适度 + sim2real 偏差 | 终极目标 |

## 7. 死胡同（v3 已最终排除，不再考虑）

| 方案 | 退出原因 |
|---|---|
| NuRec 容器 | 训练 + 推理服务闭源 docker；预训练资产全欧美且不可再分发；CARLA tutorial 当前还坏 |
| AlpaSim 作主线 | 默认 renderer 仅 NuRec；第三方 planner 接入未文档；外部独立复现 0；可保留作"对标 Alpamayo 0.81 基线"的参考 |
| WorldEngine | 实际是 4 秒 NAVSIM v2 pseudo-closed-loop demo；硬绑 nuPlan；15 commits + 0 第三方复现 + arXiv 未发；改造成中国数据 ≥2 个月 |
| SimScale 作 agent 框架 | 误读，它是 sim-real 训练辅助 |
| DriveArena | 2024-11 起半停滞 |
| 纯生成式无显式 3D（Panacea/Drive-WM） | off-trajectory 几何漂移 |
| GAIA-2/3 | 闭源 |
| LGSVL / AirSim | 已停服 / 停更 |
| 商业街景（百度/高德/腾讯） | ToS 禁止商业重训 |
| nuScenes-CN / OpenLane-V2 中国 | 不存在 |
| DAIR-V2X 作重建主源 | 路端固定相机非 ego-centric；改作 V2X 评测专用 |
| 自研 case DSL | 追平 OpenDRIVE + behavior tree + ScenarioRunner 生态需 6–12 人月，纯浪费 |
| CARLA UE5 渲染作主 | 中国资产空白；sim2real gap 大；保留作 fallback / debug |

## 8. 后续阶段（v3）

- 阶段 3（4–6 周）：单场景闭环 MVP — ONCE 单段 → DriveStudio 重建 → gsplat renderer service → CARLA gRPC bridge → SparseDrive 接入
- 阶段 4（4 周）：算法接口 + 中国 case 库（OSC 2.0）批量
- 阶段 5（4–6 周）：HUGSIM 评测 + 多算法对比 + sim2real KPI
- 阶段 6（持续）：Cosmos / Vista 作 alternative renderer，A/B 对照

## 9. 决策演化（保留作 ADR）

| 版本 | 主骨架 | 渲染 | 退出原因 |
|---|---|---|---|
| v1 (2026-05-08 上午) | AlpaSim 主 + SimScale 补 | NuRec | SimScale 误读为 agent 框架；NuRec 调研未完成 |
| v2 (同日下午) | WorldEngine 主 + AlpaSim 副 | DriveStudio + gsplat | NuRec 调研发现 docker 闭源；进一步暴露 AlpaSim 接入文档缺失 |
| **v3 (同日傍晚)** | **CARLA（headless）** | **gsplat 1.5 + DriveStudio + OmniRe** | WorldEngine 实为 4s pseudo-loop demo；CARLA gRPC 路由先例存在；OSC 2.0 case 生态成熟 |

7 个 agent 调研报告原始资料保留在 `C:\Users\elane\AppData\Local\Temp\claude\E--test-AutoSim\` 任务输出目录，可回溯。
