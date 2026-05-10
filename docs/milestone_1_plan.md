# Milestone 1 — 单轨闭环打通

> 替代已废弃的 `week1_plan.md`。本文按**任务**而非时间组织——做完即下一阶段，不卡周次。
> 目标定位见 [executive_brief.md](executive_brief.md) Phase 1，技术决策依据见 [architecture.md](architecture.md) v4-final。

---

## 1. 里程碑目标

用 **CARLA 0.9.16 (UE4) + nuScenes mini + SparseDriveV2** 打通 **场景定义 → 仿真核心 → 图像渲染 → 端到端算法 → 控制闭环 → 评测报告** 六个阶段。

### 1.1 完成判定（"数字合理"档）

| 维度 | 要求 |
|---|---|
| **链路完整性** | 六个阶段任意中间产物可单独 inspect / 离线回放 |
| **行为合理性** | 自车在 cut-in 类场景中能保持车道、不撞前车、能做出避让/减速反应 |
| **数字落地** | EPDMS 报告（HTML 或 JSON）能产出；分数本身**不要求**对齐 SparseDriveV2 论文的 90.38（CARLA 域 ≠ nuScenes 域，分数会显著低于论文） |
| **可重复** | 同一 scenario + 同一 seed 闭环结果 bit-wise 一致（CARLA sync mode + 算法 deterministic） |

### 1.2 显式排除项（**不在**本里程碑内）

- ❌ CARLA 0.10 / UE5 / Track A2
- ❌ Cosmos / Drive-Dreams / Track B
- ❌ gsplat / DriveStudio / OmniRe / Track C
- ❌ Senna / Hydra-NeXt / DiffusionDrive / DriveLM / OpenEMMA
- ❌ DAIR-V2X / ApolloScape / DrivingDojo / ONCE 数据
- ❌ Bench2Drive 全套 220 case 兼容性验证（仅借用 1 个 case 起步）
- ❌ ONCE / DAIR-V2X 全集邮件申请（不阻塞，可由用户自行另起线程并行）
- ❌ HUGSIM 真闭环

---

## 2. 总体架构（最小子集）

```
Bench2Drive cut-in case (.xosc/.py)
        │
        ▼
CARLA 0.9.16 sync mode (--RenderOffScreen)
   ego + traffic actors + PhysX
        │ tick @ 10 Hz: {ego_pose, actor_poses, hd_map, weather, t}
        ▼
ego 上挂 6 个 RGB camera (近似 nuScenes 配置)
   每 tick dump → {cam_id: HxWx3 uint8}, intrinsics, extrinsics
        │
        ▼
SparseDriveV2 plugin (e2e_plugins/sparsedrive_v2.py)
   Observation → trajectory K×3 (ego frame, dt=0.5s, K=6)
        │
        ▼
Pure Pursuit (kinematics/pure_pursuit.py)
   trajectory + ego_state → (steer, throttle, brake)
        │
        ▼
CARLA ego.apply_control() → 回到下一 tick
        │
        ▼
rollout 结束 → autosim_log → NAVSIM Scene pickle
        │
        ▼
NAVSIM v2 metric → EPDMS report (HTML)
```

---

## 3. 阶段 0：环境与依赖（前置）

> **目标机器**：A800 80G + Ubuntu 22.04 + NVIDIA driver ≥ 535 + nvidia-container-toolkit。本地 Windows 开发机不是部署目标，CARLA / SparseDriveV2 / NAVSIM 全部在 A800 机器上跑。

### 任务 0.1 Python/CUDA 环境
- [ ] 锁定 Python 3.10 + CUDA 12.1 + PyTorch 2.4（A800 是 Ampere sm_80，PyTorch 2.4 默认轮子直接吃；不需要 sm_90 编译）
- [ ] `environment.yml` 提交（conda env name: `autosim`）
- [ ] ruff + pyright + pytest 配置（`pyproject.toml`）

### 任务 0.2 CARLA docker
- [ ] 拉 `carlasim/carla:0.9.16` 镜像
- [ ] A800 headless `--RenderOffScreen` 启动 Town10，30 秒不 crash（Ubuntu 22.04 + nvidia-container-toolkit；`--gpus all`）
- [ ] 实测 fps + 显存占用记录到 `docs/milestone_1_report.md`

### 任务 0.3 数据下载
- [ ] nuScenes mini（~3GB，无审批）下载至 `data/nuscenes/mini/`
- [ ] 校验 sample/sample_data 表加载正常（用 `nuscenes-devkit` 单测）

### 任务 0.4 模型权重
- [ ] SparseDriveV2 official ckpt 下载（HF 或作者 release）
- [ ] ResNet-34 backbone 权重就绪
- [ ] 文件路径写入 `configs/sparsedrive_v2.yaml`

### 任务 0.5 Submodules
- [ ] `git submodule add carla-simulator/scenario_runner third_party/scenario_runner`
- [ ] `git submodule add Thinklab-SJTU/Bench2Drive third_party/bench2drive`
- [ ] `git submodule add swc-17/SparseDriveV2 third_party/sparsedrive_v2`

### 任务 0.6 包骨架
- [ ] 建 `src/autosim/{core,renderer/carla_ue4,kinematics,scenarios,e2e_plugins,data_adapters,eval}` 目录结构
- [ ] 各子包 `__init__.py` 占位
- [ ] `e2e_plugins/protocol.py` 已存在 ✅（无需改动）

**验收**：`pytest tests/` 空套件全绿；`docker run carlasim/carla:0.9.16 ./CarlaUE4.sh --RenderOffScreen` 不 crash；nuScenes mini `from nuscenes.nuscenes import NuScenes; NuScenes(...)` 加载成功。

---

## 4. 阶段 1：场景定义

> 策略：先用 Bench2Drive 现成 case 让后续五阶段尽快通；OSC 2.0 自写 case 作为里程碑收尾任务（任务 7.3）。

### 任务 1.1 Bench2Drive case 加载
- [ ] 选定一个 cut-in 类 case（如 `cut_in_from_left_lane`）
- [ ] 验证 case 在 CARLA 0.9.16 下能正常 spawn（如果 Bench2Drive 锁 0.9.15，先记录 ABI 兼容性结果；不兼容则切 0.9.15 docker）
- [ ] 解析 case → ego 初始 pose、route、其他 actor 行为脚本

### 任务 1.2 ScenarioRunner 接入
- [ ] ScenarioRunner 装好 + 自带 example 跑通（验证 ANTLR4 + py_trees 链路）
- [ ] 写 `src/autosim/scenarios/loader.py`：统一 case 加载入口（先支持 Bench2Drive Python 脚本格式）

**验收**：`python scripts/load_scenario.py --case cut_in_from_left_lane` 启动 CARLA 后，ego 与 cut-in 车都被 spawn，case 行为脚本驱动 cut-in 车切入主车道。

---

## 5. 阶段 2：仿真核心

### 任务 2.1 CARLA sync mode wrapper
- [ ] `src/autosim/core/carla_runtime.py`：封装 `carla.Client` + `world.tick()` 同步循环
- [ ] 固定步长 dt=0.1s（10 Hz），固定 seed 支持
- [ ] 支持 `--RenderOffScreen` 启动参数

### 任务 2.2 State 抽取
- [ ] 每 tick 抽取：ego pose (4×4)、ego velocity/yaw rate、所有 actor pose+type、当前天气、HD map (lane polylines)
- [ ] 序列化为 `dict`，落 `runs/<run_id>/states/tick_{i:04d}.pkl`
- [ ] HD map 抽取走 `world.get_map().get_topology()` + `lane.get_waypoints()`

### 任务 2.3 Traffic Manager
- [ ] 启用 TM autopilot 驱动其他车辆（除 cut-in 行为车之外）
- [ ] 行人 spawn（如 case 含行人则启用，否则跳过）

**验收**：`python scripts/run_simulation_only.py --case cut_in_from_left_lane --duration 10s --no-render` 能跑完 100 个 tick，每 tick 状态 dump 完整，回放时 actor 轨迹与 case 描述一致。

---

## 6. 阶段 3：图像渲染

### 任务 3.1 6-cam rig
- [ ] `src/autosim/renderer/carla_ue4.py`：实现 `Renderer` ABC（已在 `renderer/base.py` 定义）
- [ ] 在 ego 上 attach 6 个 `sensor.camera.rgb`，命名按 nuScenes 规范：`CAM_FRONT`, `CAM_FRONT_LEFT`, `CAM_FRONT_RIGHT`, `CAM_BACK`, `CAM_BACK_LEFT`, `CAM_BACK_RIGHT`
- [ ] 6 cam 外参近似 nuScenes（位置 ±1m、yaw ±55°/±110°/180°）；FOV/分辨率取 nuScenes 1600×900 + 70° HFOV 近似

### 任务 3.2 Frame buffer
- [ ] sync mode 下每 tick 拉取 6 路 frame（用 `sensor.listen()` + per-frame queue）
- [ ] dump 到 `runs/<run_id>/frames/tick_{i:04d}/{cam_id}.png`

### 任务 3.3 Intrinsic/extrinsic 导出
- [ ] 从 CARLA `sensor.attributes` + `sensor.get_transform()` 算 3×3 K 与 4×4 cam→ego
- [ ] **坐标系转换**：CARLA 是左手 UE 系（X 前 / Y 右 / Z 上），nuScenes 是右手系（X 右 / Y 前 / Z 上），需要在 extrinsic 中做轴交换 + 符号翻转
- [ ] 写 `src/autosim/renderer/coord_convert.py` + 单元测试（用一个已知 4×4 验证转换正确性）

**验收**：`python scripts/render_one_tick.py` 输出 6 张 PNG + `intrinsics.json` + `extrinsics.json`；用 nuScenes 工具可视化 cam pose 与 nuScenes 真车配置近似。

---

## 7. 阶段 4：端到端算法

### 任务 4.1 SparseDriveV2 standalone 推理验证
- [ ] 在 nuScenes mini 单帧上跑 SparseDriveV2 inference（用作者 demo 脚本，不接 CARLA）
- [ ] 输出 K×3 轨迹，shape 与 protocol.Action.trajectory 对齐（K=6, dt=0.5s）
- [ ] 推理耗时记录（A800 单卡 BF16 / FP16 对比；A800 无 FP8，跳过）

### 任务 4.2 SparseDriveV2 plugin adapter
- [ ] `src/autosim/e2e_plugins/sparsedrive_v2.py` 实现 `E2EPlanner` 协议（`reset`/`step`/`close`）
- [ ] `step(obs: Observation) -> Action`：把 6 cam RGB + intrinsics + extrinsics + ego_state 转成 SparseDriveV2 内部 batch 格式
- [ ] **关键转换**：图像归一化（BGR/RGB? mean/std？）、batch 维度补齐、ego_state → can_bus 字段、nav_command → command int

### 任务 4.3 Plugin 协议测试
- [ ] `tests/test_sparsedrive_v2_plugin.py`：用 nuScenes mini 一帧造 Observation → 调 plugin.step → 断言 Action 形状/类型
- [ ] dummy 输入 sanity（全黑图像、全白图像）不 crash

**验收**：`pytest tests/test_sparsedrive_v2_plugin.py -v` 全绿；CARLA 一个 tick 的 frames 喂进去能输出非 NaN 轨迹。

---

## 8. 阶段 5：控制闭环

### 任务 5.1 自行车模型
- [ ] `src/autosim/kinematics/bicycle.py`：标准自行车模型 `(x, y, heading, v, steer)` 状态推进
- [ ] 单测：定速直行 / 定转向圆周运动 解析解对比

### 任务 5.2 Pure Pursuit
- [ ] `src/autosim/kinematics/pure_pursuit.py`：输入轨迹 K×3 + 当前 ego_state → 输出 `(steer_rad, throttle [0,1], brake [0,1])`
- [ ] lookahead 距离 = 速度自适应（`L_d = max(3m, 0.5*v)`）
- [ ] 加速度 → throttle/brake 映射用简单 PID（kp=0.5）

### 任务 5.3 闭环回灌
- [ ] `scripts/run_closed_loop.py`：CARLA tick → renderer → plugin → pure_pursuit → `ego.apply_control()` → 下一 tick
- [ ] 50 tick dryrun（先用一个**返回直行轨迹的 dummy planner**验证闭环回灌通路）
- [ ] 然后切 SparseDriveV2 plugin 跑同样 50 tick，确认能跑完不 crash

**验收**：`python scripts/run_closed_loop.py --case cut_in_from_left_lane --planner sparsedrive_v2 --duration 10s` 全程 100 tick 无 crash，ego 在车道内、不出图、不抽搐。

---

## 9. 阶段 6：评测报告

### 任务 6.1 NAVSIM v2 metric 包
- [ ] `pip install navsim`（如官方 PyPI 不全则 git clone navsim 装 dev mode）
- [ ] `from navsim.metrics import EPDMS` 至少能 import

### 任务 6.2 Scene pickle adapter
- [ ] `src/autosim/eval/navsim_adapter.py`：实现 `autosim_log_to_navsim_scene(log: dict) -> navsim.Scene`
- [ ] 把每 tick 的 ego_pose / actor_poses / 6 cam frame paths / hd_map 装成 NAVSIM `Scene` pickle 字段
- [ ] 用 nuScenes mini 一段 ground truth log 反向验证 adapter 转换正确（`navsim.Scene` 加载后字段完整）

### 任务 6.3 EPDMS 计算 + 报告
- [ ] `scripts/compute_epdms.py`：load `runs/<run_id>/log.pkl` → adapter → EPDMS metric → 输出 `runs/<run_id>/epdms.json`
- [ ] HTML 报告生成（简单 jinja2 模板就够，包含：sub-metrics 分项、轨迹可视化、关键帧 6 cam 拼图）

**验收**：`python scripts/compute_epdms.py --run runs/m1_smoke` 输出 EPDMS 总分 + 9 个 sub-metric 分项 + HTML 报告；HTML 在浏览器中能打开看到关键帧 6 路画面。

---

## 10. 阶段 7：集成验收

### 任务 7.1 端到端 smoke
- [ ] `python scripts/run_milestone_1.py --case cut_in_from_left_lane` 一键跑完六阶段，产出 EPDMS 报告
- [ ] 录屏（自车视角 + 第三人称 + 6 cam 拼图）

### 任务 7.2 行为合理性人工评审
- [ ] 看录屏：cut-in 出现时自车有反应（减速 OR 让线 OR 至少不直接撞）
- [ ] 看 EPDMS 报告：NC（无碰撞）应该 = 1；DAC（车道保持）应该 > 0.5；其他分项有数字即可

### 任务 7.3 [里程碑收尾] OSC 2.0 自写 case
- [ ] 用 OSC 2.0 modifier+composition 子集写一个最小 cut-in scenario
- [ ] 走 ScenarioRunner 解析 → CARLA spawn
- [ ] 用同一套 pipeline 再跑一遍，产出第二份 EPDMS 报告
- [ ] **如 OSC 2.0 actor flow stub 阻塞复杂行为**：退到 Python API（`scenarios/<case>.py` 实现 `setup_scenario(world)`），记录退化决策到 `docs/milestone_1_report.md`

**里程碑 GREEN 判定**：任务 7.1 + 7.2 通过即视为里程碑达成；任务 7.3 视为加分项（OSC 2.0 链路验证），不阻塞 milestone 1 收尾。

---

## 11. 风险与回退

| # | 风险 | 概率 | 回退 |
|---|---|---|---|
| R1 | CARLA 0.9.16 A800 headless 偶发 crash | 低 | 官方 production 模式，预期稳定；crash 时切 `Quality=Low`，或检查 nvidia-container-toolkit + driver ≥ 535 |
| R2 | Bench2Drive 锁 0.9.15 与 0.9.16 ABI 不兼容 | 低 | 拉 0.9.15 docker 副镜像专跑 Bench2Drive case |
| R3 | SparseDriveV2 输入 schema 文档不全（adapter 字段对不上） | 中 | 读源码 `data/loaders/nuscenes.py` 对齐字段；nuScenes mini 跑通 standalone 后字段映射有 reference |
| R4 | CARLA→nuScenes 坐标系转换出错（轨迹镜像/反向） | 中 | `coord_convert.py` 单测 + 闭环可视化早发现；典型症状是车始终往一边偏 |
| R5 | NAVSIM v2 EPDMS Scene pickle 字段缺失 | 中 | 走 NAVSIM dev_kit demo 反推必填字段；预留 1 周工作量给 adapter |
| R6 | OSC 2.0 actor flow 是 stub | 高 | 任务 7.3 退到 Python API（v4-final D5 已认可此路径）|
| R7 | SparseDriveV2 在 CARLA 域上"乱开"（cross-domain 严重） | 中 | 接受现象（这是预期的，论文 90.38 是 nuScenes 域内分数）；只要 NC ≈ 1、不撞车即合格 |

---

## 12. 交付物清单

里程碑结束后仓库应有：

- `src/autosim/core/carla_runtime.py` — CARLA sync wrapper
- `src/autosim/renderer/carla_ue4.py` — Track A1 实现
- `src/autosim/renderer/coord_convert.py` — 坐标系转换
- `src/autosim/e2e_plugins/sparsedrive_v2.py` — SparseDriveV2 adapter
- `src/autosim/kinematics/{bicycle,pure_pursuit}.py`
- `src/autosim/scenarios/loader.py` — Bench2Drive + OSC 2.0 + Python API 统一入口
- `src/autosim/eval/navsim_adapter.py` — Scene pickle adapter
- `scripts/run_milestone_1.py` — 一键端到端
- `tests/` — 至少 plugin、coord_convert、bicycle 各一组单测
- `runs/m1_smoke/` — Bench2Drive case 完整 rollout + EPDMS 报告
- `runs/m1_osc2/` — OSC 2.0 自写 case rollout + EPDMS 报告（如任务 7.3 通过）
- `docs/milestone_1_report.md` — 实测踩坑、回退决策、关键截图

---

## 13. 后续

里程碑达成后，下一步选项（**不在本计划范围**）：

- **拓展数据**：DAIR-V2X-V example / ApolloScape 北京段接入 → Phase 2 中国 case 库起步
- **拓展轨道**：Track B (Cosmos) / Track C (gsplat) 接入 → 四轨道对照
- **拓展算法**：Senna / Hydra-NeXt 接入 → 多算法横评
- **场景库**：Bench2Drive 220 case 全跑 + OSC 2.0 自写中国 case
