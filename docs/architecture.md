# AutoSim 架构 v4-final

> 2026-05-09，方向最终锁定。基于 13 个并行 SOTA 调研 + 4 轮架构反转 + 2 轮落地 sanity check。
> **项目性质：自研、非商用。** 离线批跑（不要求实时）。

## 0. 决策摘要

| # | 决策 | 选定 | 评级 |
|---|---|---|---|
| D1 | 闭环骨架 | **CARLA 0.9.16 (UE4) 主 + CARLA 0.10 (UE5) 副双轨** | 🟡 |
| D2 | MVP E2E 算法 | **SparseDriveV2 主 + Senna 副**；后续横评 Hydra-NeXt / DiffusionDrive / DriveLM / OpenEMMA | 🟢/🟡 |
| D3 | 首个数据 | **nuScenes mini（免审批 MVP）+ ApolloScape 北京 + DrivingDojo HF**；ONCE / DAIR-V2X 并行申请不阻塞 | 🟢 |
| D4 | 渲染层（四轨道并列） | A1=CARLA UE4 / A2=CARLA UE5 / B=Cosmos 双 backend (B-cn=Predict2.5-2B+DrivingDojo LoRA + B-av=Drive-Dreams-7B；**串行不并行**) / C=gsplat+DriveStudio | 🟢 |
| D5 | Case 编辑 | OpenSCENARIO 2.0 + ScenarioRunner；actor flow 可能是 stub | 🟡 |
| D6 | 渲染路由 | Renderer Python ABC（无 gRPC） | 🟢 |
| D7 | 评测脚手架 | NAVSIM v2 metric + Scene pickle adapter（~1 周）+ HUGSIM 副线 | 🟡 |
| D8 | 阶段策略 | Phase 1 A1 单轨 → Phase 2 四轨 → Phase 3 HUGSIM + 中国 case | 🟢 |

## 1. 整体架构

```
┌── Case 描述层 ─────────────────────────────────────────────────┐
│  OSC 2.0 文件 (ScenarioRunner 解析)                            │
│  + Bench2Drive 220 case（兼容 0.9.15/0.9.16，免费继承）        │
│  + 自写中国 case（OSC 2.0 modifier+composition；actor flow     │
│    退 Python API）                                              │
└───────────────────┬────────────────────────────────────────────┘
                    │
                    ▼
┌── Scenario Runtime ────────────────────────────────────────────┐
│  CARLA 0.9.16 synchronous mode + --RenderOffScreen             │
│  Traffic Manager + behavior tree + PhysX                       │
│  per-tick dump: {HDMap, ego_pose, actor_poses, weather, t}     │
│  CARLA 0.10 (UE5) 仅作 A2 轨道 renderer 使用，不作 runtime     │
└───────────────────┬────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┬───────────────┬──────────────┐
        ▼                       ▼               ▼              ▼
┌── Track A1 ───┐      ┌── Track A2 ──┐  ┌── Track B (双 backend, 串行) ──┐  ┌── Track C ──┐
│ CARLA UE4     │      │ CARLA UE5     │  │ B-cn: Predict2.5-2B            │  │ gsplat 3DGUT │
│ (0.9.16)      │      │ (0.10)        │  │       + DrivingDojo LoRA       │  │ + DriveStudio│
│               │      │               │  │       (中国感主报告)            │  │ + ONCE/Apollo│
│ 几何 baseline │      │ 视觉升级实验  │  │ B-av: Drive-Dreams-7B          │  │   重建        │
│ Bench2Drive   │      │ Lumen+Nanite  │  │       (HD map+bbox→multi-view) │  │ (sim2real    │
│   兼容        │      │ (dead branch  │  │       AV 基座对照               │  │  黄金对照)   │
│               │      │   风险已知)   │  │ Vista 双失败时 fallback        │  │               │
└─────┬─────────┘      └──────┬───────┘  └──────────┬─────────────────────┘  └──────┬──────┘
      │ RGB                   │                 │                │
      └──────────┬────────────┴─────────────────┴────────────────┘
                 ▼
┌── E2E 算法层（Plugin Protocol，已落地） ─────────────────────┐
│  MVP 主: SparseDriveV2 (Apache, NAVSIMv2 90.38 EPDMS) ⭐      │
│  MVP 副: Senna (Apache, 自建 NAVSIM v2 harness)               │
│  横评: Hydra-NeXt / DiffusionDrive / DriveLM / OpenEMMA       │
└────────────────────┬─────────────────────────────────────────┘
                     │ trajectory K×3
                     ▼
              自行车模型 + Pure Pursuit / LQR
                     │ steer/throttle
                     └─→ CARLA apply_control() 闭环回灌

┌── 评测层 ──────────────────────────────────────────────────────┐
│  EPDMS（NAVSIM v2 metric 库 + 自建 Scene pickle adapter）       │
│  四轨道一致性（A1/A2/B/C 同算法 PDMS 分差，v4-final 独创）      │
│  HUGSIM HD-Score（Phase 3 真闭环对照）                         │
└───────────────────┬────────────────────────────────────────────┘
                    ▼
              测试报告 (HTML/PDF)
        case × 算法 × renderer 三维矩阵
```

## 2. 目录结构

```
AutoSim/
├── README.md
├── requirements.txt
├── docs/
│   ├── architecture.md          # 本文
│   └── milestone_1_plan.md      # 第一个里程碑（单轨闭环）
├── src/
│   └── autosim/
│       ├── core/                # CARLA synchronous wrapper、tick 循环
│       ├── renderer/            # Renderer ABC + 四个实现
│       │   ├── base.py          # 抽象基类 (renderer Protocol)
│       │   ├── carla_ue4.py     # Track A1
│       │   ├── carla_ue5.py     # Track A2
│       │   ├── cosmos.py        # Track B
│       │   └── gsplat_3dgut.py  # Track C
│       ├── training/            # DriveStudio + OmniRe 训练入口（薄封装）
│       ├── world_model/         # Cosmos / Vista LoRA FT 工具
│       ├── kinematics/          # 自行车模型、Pure Pursuit、LQR
│       ├── scenarios/           # OSC 2.0 case 加载 + 中国 case 库
│       ├── e2e_plugins/         # 统一插件协议 + 各算法 adapter
│       │   ├── protocol.py      # ★ 已落地
│       │   ├── sparsedrive_v2.py
│       │   ├── senna.py
│       │   └── ...
│       ├── data_adapters/       # 数据集 → DriveStudio 内部格式
│       │   ├── nuscenes.py
│       │   ├── once.py          # 等审批通过后启用
│       │   ├── dair_v2x_v.py
│       │   ├── apolloscape.py
│       │   └── drivingdojo.py
│       └── eval/                # NAVSIM v2 + HUGSIM 评测钩子
│           └── navsim_adapter.py # ★ Scene pickle adapter（~1 周工作量）
├── scripts/
│   ├── reconstruct_scene.py     # 数据 → 3DGS 资产
│   ├── run_closed_loop.py       # CARLA + Renderer + Plugin 闭环
│   └── benchmark_e2e.py
├── scenarios/
│   ├── chinese/                 # 自写中国 case（OSC 2.0 + Python API mix）
│   └── examples/
├── tests/
└── third_party/                 # git submodule
    ├── scenario_runner/
    ├── drivestudio/
    ├── sparsedrive_v2/
    ├── senna/
    ├── hugsim/
    └── cosmos-predict2.5/       # 通过 HF 自动拉，不必 submodule
```

## 3. 关键接口

### 3.1 E2E 算法插件（已落地）

见 [`src/autosim/e2e_plugins/protocol.py`](../src/autosim/e2e_plugins/protocol.py)。仿真器只消费 `Action.trajectory`，由 `kinematics/` 的 Pure Pursuit 输出 control 调 CARLA `apply_control()`。

### 3.2 Renderer Python ABC（v4-final 简化，无 gRPC）

```python
# src/autosim/renderer/base.py
from typing import Protocol
import numpy as np

class Renderer(Protocol):
    def load_scene(self, scene_id: str) -> None: ...
    def render(
        self,
        camera_poses: dict[str, np.ndarray],   # {cam_id: 4x4}
        intrinsics: dict[str, np.ndarray],
        actors: list[dict],                    # [{id, pose, type, ...}]
        weather: str,
        timestamp: float,
    ) -> dict[str, np.ndarray]:                # {cam_id: HxWx3 RGB}
        ...
```

四个实现（`carla_ue4.py` / `carla_ue5.py` / `cosmos.py` / `gsplat_3dgut.py`）各自填这个接口。仿真器主循环只看 `Renderer`，与具体后端无关。

### 3.3 NAVSIM v2 Scene pickle adapter（v4-final 新增工作量）

NAVSIM v2 的 EPDMS 不能 `from navsim.metrics import EPDMS` 直接调，必须把自定义 scenario 转成 NAVSIM 的 `Scene` pickle 协议。`src/autosim/eval/navsim_adapter.py` 完成：

```python
def autosim_log_to_navsim_scene(autosim_log: dict) -> "navsim.Scene":
    """把我们闭环 rollout 的日志转成 NAVSIM 的 Scene pickle 格式
       供 EPDMS 计算。"""
    ...
```

预估 ~1 人周。

### 3.4 Scenario YAML / OSC 2.0 schema（Phase 2 落地）

case 直接写 OSC 2.0 文件；AutoSim 这边 `scenarios/<case>.osc` + `scenarios/<case>.meta.yaml`。actor flow 受限时退 Python API：`scenarios/<case>.py` 实现 `setup_scenario(world)`。

## 4. 数据流（单 tick，10 Hz 慢跑离线）

```
t=k:
  carla.tick()                                 # 推进 PhysX + agent
  state = carla.get_world_snapshot()
  for renderer in [A1, A2, B, C]:              # 四轨道 (可并行)
      obs[renderer] = renderer.render(state)
  # 主轨道决定下一步：
  action = planner.step(obs[active_track])
  control = pure_pursuit(action.trajectory, ego.state)
  carla.ego_vehicle.apply_control(control)
  for renderer in non_active:                  # 副轨道仅记录
      log_obs(renderer, obs[renderer])
  eval.log(t, ego, action, gt)
t=k+1
```

## 5. 已识别风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|---|
| R1 | gsplat 3DGUT 与 DriveStudio MCMC strategy 不兼容 | 中 | 中 | W1 验证；切 strategy 或 fork 后修补 |
| R2 | 中国数据 LiDAR 不密 → 几何先验差 | 中 | 高 | patch SplatAD LiDAR loss；ApolloScape LiDAR 较密兜底 |
| R3 | rolling shutter timestamp 同步不全 | 中 | 中 | 重对齐；W2 评估再决定是否启用 RS |
| R4 | OSC 2.0 actor flow 是 stub | 高 | 中 | 复杂场景退 Python API；用 modifier+composition 子集 |
| R5 | OSC 2.0 解析强依赖 carla.* | 低 | 低 | 既然 CARLA 必装无影响 |
| R6 | ONCE 申请超 60 天 / DAIR-V2X 邮件不回 | 中 | 中 | nuScenes mini + ApolloScape + DrivingDojo HF 兜底；不阻塞 Phase 1 |
| R7 | DriveStudio ONCE adapter 工作量 | 中 | 低 | ~1 人周已计入 |
| R8 | Bench2Drive 锁 0.9.15，要求 0.9.16 | 低 | 低 | 0.9.15 与 0.9.16 通常 ABI 兼容；冲突时拉 0.9.15 docker 副镜像 |
| R9 | CARLA 0.9.16 RenderOffScreen 在 H100 不稳定 | 低 | 中 | 官方支持模式；W1 hello-world 验证 |
| R10 | SparseDriveV2 / Senna 在中国数据上未公开评测 | 中 | 低 | 先 nuScenes 权重做迁移；必要时 FT |
| R11 | **CARLA 0.10 是 dead branch（17 个月无 patch）** | 高 | 低 | A2 标记为"实验性"，A1 才是 production；如 W1 验证 0.10 失败立即退场 |
| R12 | **NAVSIM v2 metric 不能裸 import** | 已知 | 低 | Scene pickle adapter ~1 周已计入 D7 |
| R13 | Senna 论文只 nuScenes 报点，无 NAVSIM v2 数字 | 已知 | 低 | 自建 harness ~1 周；先用 SparseDriveV2 出第一份报告 |
| R14 | Cosmos HF 国内访问不稳 | 中 | 低 | HF 镜像 / 代理；权重 32GB 一次性下载 |

## 6. 评测指标（多 benchmark 联评）

| Benchmark | 协议 | 关键指标 | 用途 |
|---|---|---|---|
| NAVSIM v2 metric (借用) | Scene pickle adapter 接入 | EPDMS (NC/DAC/DDC/TLC × EP/TTC/LK/HC/EC) | 主报告，社区可比 |
| Bench2Drive (CARLA 0.9.16 直接复用) | CARLA 闭环 | DS（Driving Score） | 算法绝对能力 sanity check |
| 四轨道一致性（v4-final 独创） | 同 case × 4 renderer × 同算法 | EPDMS 方差 / KL(轨迹分布) | 跨渲染域鲁棒性，paper 角度 |
| HUGSIM (Phase 3) | 70 序列 + extrapolated KID | HD-Score | sim2real 真闭环对照 |

## 7. 死胡同（v4-final 已最终排除）

| 方案 | 退出原因 |
|---|---|
| NuRec 容器 | 训练管线 + 推理服务全闭源 docker；CARLA tutorial 还坏 |
| AlpaSim 作主线 | 默认 renderer 仅 NuRec；第三方 planner 接入未文档；外部独立复现 0 |
| WorldEngine | 4s NAVSIM v2 pseudo-loop demo；硬绑 nuPlan；arXiv 未发；改造 ≥2 月 |
| SimScale 作 agent 框架 | 误读，是 sim-real 训练辅助 |
| DriveArena | 2024-11 起半停滞 |
| 纯生成式无显式 3D（Panacea/Drive-WM） | off-trajectory 几何漂移 |
| GAIA-2/3 | 闭源 |
| LGSVL / AirSim | 已停服 / 停更 |
| 商业街景（百度/高德/腾讯） | ToS 禁止（自研也按这边界） |
| nuScenes-CN / OpenLane-V2 中国 | 不存在 |
| DAIR-V2X 作重建主源 | 路端固定相机非 ego-centric；V 子集 22k 帧可作辅助 |
| 自研 case DSL | 追平 OpenDRIVE + ScenarioRunner 生态需 6–12 人月 |
| MetaDrive / Scenic / Waymax 替代 CARLA | 既然 UE 渲染要保留，CARLA 必装；多此一举 |
| ScenarioRunner standalone | OSC 2.0 解析强依赖 carla.* 模块 |

## 8. 阶段计划

- **Phase 1 (W1–W6)**：A1 单轨 + nuScenes mini + SparseDriveV2 → 第一份 EPDMS 报告。包含 W1 五个 hello-world + DAIR-V2X-V example 子集。
- **Phase 2 (W7–W12)**：四轨对照（A1+A2+B+C）+ ApolloScape 北京 + DrivingDojo LoRA + Senna 接入 + 中国 case 库（OSC 2.0 + Python API mix） → 三维矩阵报告。
- **Phase 3 (W13+)**：HUGSIM 真闭环 + ONCE 数据（如已审批）+ ReconDreamer++ off-traj 修复。

## 9. 决策演化（保留作 ADR）

| 版本 | 主骨架 | 渲染 | 触发反转 |
|---|---|---|---|
| v1 (2026-05-08 上午) | AlpaSim + SimScale | NuRec | SimScale 误读为 agent 框架；NuRec 调研未完 |
| v2 (同日下午) | WorldEngine + AlpaSim | DriveStudio + gsplat | NuRec 闭源 docker 暴露；AlpaSim 第三方 planner 接入文档缺失 |
| v3 (同日傍晚) | CARLA headless | gsplat 主 + Cosmos 副 | WorldEngine 是 4s pseudo-loop demo |
| v4 (同日深夜) | NAVSIM v2 + 三 renderer | Cosmos 主 + gsplat 副 + CARLA UE | 用户加"离线批跑"约束；NAVSIM v2 协议与目标完美对齐；三 renderer 对照成形 |
| **v4-final (2026-05-09)** | **CARLA 0.9.16 + 0.10 双轨 + NAVSIM v2 metric + 四 renderer** | **A1+A2+B+C** | **sanity check：CARLA 0.10 死分支风险（保留作 A2）；自研非商用约束放松所有许可担忧；nuScenes mini 作 MVP 首数据避审批；NAVSIM v2 不能裸 import EPDMS** |
| **v4-final + D4.1 (2026-05-10)** | 同上 | A1+A2+**B(B-cn+B-av)**+C | **Track B 拆双 backend 串行**：B-cn (Predict2.5+LoRA→中国感) + B-av (Drive-Dreams→AV 高质量基座对照)；多卡放宽后用户确认串行不并行（无延迟约束 + 显存独占更稳）；Drive-Dreams 已 post-trained 在 RDS-HQ，与通用基座+LoRA 形成有意义对照 |

13 个 agent 调研报告原始资料保留在 `C:\Users\elane\AppData\Local\Temp\claude\E--test-AutoSim\` 任务输出目录。
