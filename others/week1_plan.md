> ⚠️ **已废弃 (2026-05-10)**：本文档按"周"组织、且把 gsplat / Cosmos / Senna / DAIR-V2X 等全部塞进 W1，与"先打通单轨闭环"的实际目标不匹配。
> 已被 [milestone_1_plan.md](milestone_1_plan.md) 替代——后者按**任务**而非**时间**组织，并严格收敛到 CARLA UE4 + nuScenes mini + SparseDriveV2 单轨子集。
> 本文保留作历史/调研痕迹，不再维护，不要据此执行。

---

# Week 1 任务清单（v4-final）

> 起点：仓库为空。
> 终点：5 个 hello-world 全部 GREEN + DAIR-V2X-V example 重建可视化 + 第一份 dummy EPDMS 报告。
> 约束：用户当前不要求执行，本计划是"启动后第一周可执行的"参考。
> **数据策略**：MVP 用免审批数据（nuScenes mini + DAIR-V2X-V example），ONCE / DAIR-V2X 全集申请并行启动但不阻塞。

## 周目标（DoD）

- [ ] CARLA 0.9.16 H100 headless docker 跑通无 crash（A1 GREEN）
- [ ] CARLA 0.10 H100 headless 同上验证（A2 GREEN 或退场）
- [ ] Senna standalone 单图推理跑通；vicuna-7b / LLaVA 依赖闭环
- [ ] Cosmos-Predict2.5-2B HF 下载 + BF16 推理一段 5s 视频
- [ ] ScenarioRunner OSC 2.0 cut-in minimal 跑通；探测 actor flow 是否 stub
- [ ] DAIR-V2X-V example 子集下载 + SfM 预处理 + DriveStudio 单段重建跑通
- [ ] gsplat 3DGUT 模式 hello world（在重建产物上推理）
- [ ] SparseDriveV2 nuScenes mini 单帧推理跑通，输出 K×3 轨迹
- [ ] `e2e_plugins/sparsedrive_v2.py` adapter + `tests/test_protocol.py` 全绿
- [ ] `eval/navsim_adapter.py` 雏形（dummy log → Scene pickle）
- [ ] `docs/week1_report.md` 记录每日实测延迟、踩坑、回退

## 按天

### Day 0（启动日）— 数据申请并行启动
- [ ] 发邮件：ONCE 申请（once-for-auto-driving.github.io 表单）
- [ ] 发邮件：DAIR-V2X 全集申请（dair@air.tsinghua.edu.cn）
- [ ] 接受 DrivingDojo HF 条款（自动）
- [ ] 下载 nuScenes mini（~3GB，无审批）
- [ ] 下载 DAIR-V2X-V example 子集（Google Drive）
- [ ] 下载 ApolloScape 北京段（自研非商用 OK）

### Day 1（周一）— 项目骨架 + CARLA hello-world (A1+A2)
- [ ] 锁定 Python 3.10 + CUDA 12.1 + PyTorch 2.4 环境（云上 H100 单机）
- [ ] 建 conda env（`environment.yml` 提交）
- [ ] 建立 `src/autosim/{core,renderer/{base,carla_ue4,carla_ue5,cosmos,gsplat_3dgut},training,world_model,kinematics,scenarios,e2e_plugins,data_adapters,eval}` 包骨架
- [ ] 配 ruff + pyright + pytest
- [ ] **Hello-world 1**: 拉 `carlasim/carla:0.9.16` docker，--RenderOffScreen + Town10 30s 跑通
- [ ] **Hello-world 2**: 拉 `carlasim/carla:0.10.0` 同上；如 fps < 5 或 crash 立即标 A2 RED
- [ ] 产出：`docs/week1_report.md` 第 1 节，记录两个版本实测 fps + crash 率

### Day 2（周二）— ScenarioRunner OSC 2.0 + Bench2Drive
- [ ] 拉 ScenarioRunner（git submodule add `carla-simulator/scenario_runner`）
- [ ] **Hello-world 5**: 跑官方 OSC 2.0 cut-in minimal example，确认 ANTLR4 + py_trees 链路
- [ ] 探测：actor flow / parameterized scenario 哪些是 stub（OSC 2.0 doc 列的 modifier+composition 跑一遍）
- [ ] 拉 Bench2Drive（git submodule add `Thinklab-SJTU/Bench2Drive`）
- [ ] 跑一个 Bench2Drive case (例如 cut_in)，确认与 0.9.16 兼容（README 说锁 0.9.15，验证是否 ABI 兼容）
- [ ] Python API 拉 ego pose、actor poses、HDMap，验证 50–100 Hz state stream

### Day 3（周三）— gsplat + DriveStudio 单段重建
- [ ] `pip install gsplat>=1.5.0`
- [ ] 跑 `examples/simple_trainer.py` 在 Mip-NeRF360 garden（验证 CUDA 编译）
- [ ] 跑 `examples/simple_viewer_3dgut.py`，验证 3DGUT 模式
- [ ] 拉 DriveStudio（git submodule add `ziyc/drivestudio`）
- [ ] **Hello-world 6**: nuScenes mini OmniRe 训练（~1h H100），产物喂回 gsplat 渲染
- [ ] **Hello-world 7**: DAIR-V2X-V example 子集 SfM + DriveStudio 重建（验证中国数据可吃）
- [ ] 写 `src/autosim/renderer/gsplat_3dgut.py` 雏形：load `.pt` + `render()` 接口
- [ ] **风险点 R1**: 3DGUT MCMC vs DriveStudio split/clone 不兼容；如撞上先用普通 3DGS

### Day 4（周四）— Cosmos + Senna hello-world
- [ ] **Hello-world 4**: HF 登录 → 接受 Cosmos-Predict2.5-2B OML 协议 → 拉 32GB 权重（国内 mirror 验证）
- [ ] BF16 推理一段 5s ftheta 多视频，记录延迟
- [ ] 写 `src/autosim/renderer/cosmos.py` 雏形（layout → video）
- [ ] **Hello-world 3**: 拉 Senna（git submodule add `hustvl/Senna`）+ HF 拉 `rb93dett/Senna` 权重
- [ ] 验证 vicuna-7b-v1.5 / LLaVA-v1.6 数据生成依赖能装上
- [ ] 单图（nuScenes front-cam）推理，输出 meta-action

### Day 5（周五）— SparseDriveV2 + Plugin Protocol + NAVSIM adapter
- [ ] 拉 SparseDriveV2（git submodule add `swc-17/SparseDriveV2`）+ 下载 ResNet-34 权重
- [ ] 在 nuScenes mini 单帧上 inference，输出 `K×3` 轨迹
- [ ] 完成 `e2e_plugins/sparsedrive_v2.py` adapter
- [ ] `tests/test_protocol.py`：dummy obs 调一次 step，断言 shape
- [ ] **关键工作**: `src/autosim/eval/navsim_adapter.py` 雏形——dummy log → NAVSIM Scene pickle
- [ ] `scripts/run_closed_loop_dryrun.py`：50 步 dummy 闭环（CARLA → A1 renderer → SparseDriveV2 → fake control → CARLA）
- [ ] 跑出第一份 dummy EPDMS 报告

## 验收

- 5 个 hello-world 全部 GREEN（如 A2/Cosmos 任一 YELLOW 须有缓解方案）
- DAIR-V2X-V example 重建视频可看
- 第一份 dummy EPDMS 报告（数字不重要，pipeline 通即可）
- `docs/week1_report.md` 完整记录踩坑与决策

## 已知阻塞与回退

| 阻塞 | 概率 | 回退 |
|---|---|---|
| ONCE / DAIR-V2X 申请超期 | 中 | nuScenes mini + DAIR-V2X-V example + ApolloScape + DrivingDojo HF 兜底（**Phase 1 不阻塞**） |
| CARLA 0.10 H100 headless 崩 | 中 | A2 退场，0.9.16 单独作 A 轨道（不影响整体架构） |
| Bench2Drive 0.9.15 与 0.9.16 不兼容 | 低 | 拉 0.9.15 docker 副镜像；A1 主跑 0.9.16，Bench2Drive 单独跑 0.9.15 |
| gsplat 3DGUT MCMC 与 DriveStudio 冲突 | 中 | 普通 3DGS 模式过 W1；W2 修 |
| Cosmos HF 国内下载慢/失败 | 中 | HF 镜像；如不行先用 Vista 替代占位 |
| Senna 依赖（vicuna/LLaVA）装不上 | 中 | SparseDriveV2 单独作 MVP；Senna 推到 W2 |
| OSC 2.0 actor flow 是 stub | 高 | 复杂场景退 Python API（已计入 R4） |

## Week 2 预告

- ApolloScape 北京段重建
- Cosmos LoRA on DrivingDojo（~32 GPU·h）
- Senna NAVSIM v2 harness
- 第一个完整 v4 闭环：A1 + nuScenes mini + SparseDriveV2 + EPDMS 真报告
