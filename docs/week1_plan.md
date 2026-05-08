# Week 1 任务清单（v3）

> 起点：仓库为空。
> 终点：四个核心组件各自跑通 + 一份 CARLA→gsplat gRPC bridge 的 protobuf 草案。
> 约束：用户当前不要求执行，本计划是"启动后第一周可执行的"参考；正式开工前可再调整。

## 周目标（DoD）

- [ ] CARLA 0.10 docker 跑通；ScenarioRunner 跑一个 OSC 2.0 example case（pure 逻辑层，--RenderOffScreen）
- [ ] gsplat 1.5 安装；`simple_trainer` + `simple_viewer_3dgut` 在 Mip-NeRF360 demo data 上跑通
- [ ] DriveStudio 安装；nuScenes mini 单段（~30s）重建跑通；产物 .pt 喂回 gsplat 渲染验证
- [ ] SparseDrive 在 nuScenes mini 单帧推理跑通，输出可视化轨迹
- [ ] `e2e_plugins/sparsedrive.py` adapter + `tests/test_protocol.py` 全绿
- [ ] `proto/renderer.proto` 草案完成（fork NuRec 接口结构）
- [ ] `docs/week1_report.md` 记录每日实测延迟、踩坑、回退

## 按天

### Day 1（周一）— 项目骨架 + 数据/基础环境
- [ ] 锁定 Python 3.10 + CUDA 12.1 + PyTorch 2.4 环境（云上 H100 单机起步）
- [ ] 建 conda env（`environment.yml` 提交）
- [ ] 建立 `src/autosim/{core,bridges,renderer,training,world_model,kinematics,scenarios,e2e_plugins,data_adapters,eval}` 包骨架
- [ ] 配 ruff + pyright + pytest
- [ ] **ONCE 数据申请提交**（once-for-auto-driving.github.io，学术许可，预计 1–3 天）
- [ ] CARLA 0.10 docker pull（`carlasim/carla:0.10.0`）
- [ ] 兜底：ApolloScape 北京段单 sample（无审批）+ nuScenes mini（10 段开放下载）

### Day 2（周二）— CARLA 逻辑层 + ScenarioRunner
- [ ] CARLA server 起 `--RenderOffScreen`，验证 `no_rendering_mode=True` 下物理/agent 仍跑
- [ ] 拉 ScenarioRunner（git submodule add `carla-simulator/scenario_runner`）
- [ ] 选一个 Bench2Drive / Leaderboard 2.0 example case（建议 cut_in），跑通
- [ ] 用 Python API 拉 ego pose、actor poses、weather、HDMap，验证 50–100 Hz state stream
- [ ] 写第一个最小 OSC 2.0 case：直行 + 一辆 NPC 加塞，跑通

### Day 3（周三）— gsplat 渲染栈
- [ ] `pip install gsplat>=1.5.0`
- [ ] 跑 `examples/simple_trainer.py` 在 Mip-NeRF360 garden 数据上（验证 CUDA 编译正确）
- [ ] 跑 `examples/simple_viewer_3dgut.py`，验证 3DGUT 模式可推理
- [ ] 写 `src/autosim/renderer/gsplat_renderer.py` 雏形：构造期 load `.pt`，`render(camera_poses, K, distortion)` 返回 RGB
- [ ] 单元测试：随机 GS + 随机 pose，断言能 render 出非黑图

### Day 4（周四）— DriveStudio + 单段重建
- [ ] 拉 DriveStudio（git submodule add `ziyc/drivestudio`）+ 安装依赖
- [ ] 跑作者提供的 nuScenes mini OmniRe 训练（~1h H100）
- [ ] 把训练产物喂回 Day 3 的 `gsplat_renderer.py`，验证渲染原轨迹一致性
- [ ] **风险点**：3DGUT MCMC vs DriveStudio split/clone 不兼容（R1）。如撞上：先改用普通 3DGS 模式过 Week 1，3DGUT 留 Week 2 处理

### Day 5（周五）— SparseDrive + Plugin Protocol + bridge proto
- [ ] 拉 SparseDrive，下载 nuScenes 预训练权重
- [ ] 在 nuScenes mini 单帧上跑通 inference，输出 `K×3` 轨迹
- [ ] 完成 `e2e_plugins/sparsedrive.py` adapter：`Observation` → SparseDrive 输入张量；输出 → `Action`
- [ ] `tests/test_protocol.py`：dummy obs 调一次 step，断言 shape
- [ ] `scripts/run_closed_loop_dryrun.py`：50 步 dummy 闭环（CARLA → fake renderer → SparseDrive → fake control → CARLA）
- [ ] 写 `proto/renderer.proto` 草案（参考 `docs.nvidia.com/nurec/api/grpc_api_guide.html`）

## 验收

- 提交里至少：CARLA OSC 闭环视频（即使是 UE5 渲染，验证逻辑层）、gsplat 渲染图、SparseDrive 推理可视化、`pytest` 全绿、`renderer.proto`
- `docs/week1_report.md` 记录踩坑与决策

## 已知阻塞与回退

| 阻塞 | 概率 | 回退 |
|---|---|---|
| ONCE 审批超 5 天 | 中 | 改 ApolloScape 北京段；nuScenes mini 仍可作 DriveStudio 验证（D4 不变） |
| gsplat 3DGUT MCMC 与 DriveStudio 冲突（R1） | 中 | 临时切普通 3DGS；Week 2 再修 |
| CARLA 0.10 UE5 不稳定 | 低 | 退到 0.9.16（NuRec docker 不用，但 ScenarioRunner 接口稳定） |
| SparseDrive 必须 LiDAR | 低 | 用作者 vision-only 配置；如无，临时换 UniAD |

## Week 2 预告

- ONCE 数据 adapter（照 nuScenes 写）+ 单段重建跑通
- gRPC bridge（`bridges/carla_renderer_bridge.py`）实装
- 第一个完整 v3 闭环 demo：CARLA(headless) → gRPC → gsplat(ONCE 中国场景) → SparseDrive → CARLA
