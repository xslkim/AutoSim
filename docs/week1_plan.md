# Week 1 任务清单

> 起点：仓库为空。
> 终点：DAIR-V2X 单段重建可视化 + SparseDrive 单帧推理 + Plugin Protocol 通过 dummy 调用。

## 周目标（DoD）

- [ ] DriveStudio 在 DAIR-V2X 单段（≤200m）上完成 3DGS 重建，渲染原轨迹视频肉眼可看
- [ ] CARLA 0.9.16 + NuRec 能加载上一步导出的 USD 资产并复现轨迹
- [ ] SparseDrive 在 nuScenes mini 单帧推理跑通，输出可视化轨迹
- [ ] `e2e_plugins/protocol.py` + `sparsedrive.py` adapter 完成；用 dummy obs 调一次 step 拿到合法 Action
- [ ] 项目骨架 + CI 基本（lint + 类型检查）就绪

## 按天

### Day 1（周一）— 项目骨架与数据获取
- [ ] 锁定 Python 3.10 + CUDA 12.1 + PyTorch 2.4 环境（云上 H100 单机起步）
- [ ] 建 conda env（`environment.yml` 提交）
- [ ] 建立 `src/autosim/{core,renderer,world_model,offtraj,kinematics,agents,scenarios,e2e_plugins,data_adapters,eval}` 包骨架
- [ ] 配 ruff + pyright + pytest
- [ ] **DAIR-V2X 数据申请提交**（github.com/AIR-THU/DAIR-V2X，需邮件审批，预计 2–3 天）
- [ ] 兜底：本地下载 ApolloScape 单段（无审批）作为 plan B

### Day 2（周二）— DriveStudio 重建
- [ ] 拉 DriveStudio：`git submodule add https://github.com/ziyc/drivestudio third_party/drivestudio`
- [ ] 安装依赖（gsplat, nerfacc, COLMAP）
- [ ] 写 `data_adapters/dair_v2x.py`（V2X-SPD → DriveStudio 数据格式：图像、内外参、ego pose、可选 LiDAR）
- [ ] 在 1 段（车端单 trip ~30s）上完成重建：训练 ~1h
- [ ] 渲染原始轨迹视频；目检 PSNR / 几何

**阻塞回退**：如 DAIR-V2X 仍未拿到，改用 ApolloScape 北京段做同样流程。

### Day 3（周三）— NuRec 与 CARLA 集成
- [ ] CARLA 0.9.16 Docker 拉取
- [ ] 跑通官方 NuRec 示例（确认 GPU + 驱动栈正确）
- [ ] 写脚本把 Day 2 的 DriveStudio GS 资产导出为 USD / NuRec 兼容格式
- [ ] 在 CARLA-NuRec 内复现原轨迹；目检渲染一致性
- [ ] **风险点**：NuRec 期望的 fisheye/rolling shutter 元数据是否齐全；如不齐用 `3DGUT` 默认 pinhole

### Day 4（周四）— SparseDrive 推理
- [ ] 拉 SparseDrive：`git submodule add https://github.com/swc-17/SparseDrive third_party/sparsedrive`
- [ ] 下载官方 nuScenes 预训练权重
- [ ] 在 nuScenes mini 单帧上跑通 inference，输出 `K×3` 轨迹
- [ ] 可视化：把 trajectory 画到 BEV + 前视相机上
- [ ] 测延迟（目标 H100 ≥ 9 FPS）

### Day 5（周五）— Plugin Protocol 落地
- [ ] 完成 `e2e_plugins/sparsedrive.py` adapter：`Observation` → SparseDrive 输入张量；SparseDrive 输出 → `Action`
- [ ] 写 `tests/test_protocol.py`：构造 dummy `Observation`（随机图像 + 假内外参 + ego_state），调一次 `step()`，断言 `trajectory.shape == (K, 3)`
- [ ] 写 `scripts/run_closed_loop_dryrun.py`：50 步 dummy 闭环（无渲染、无车辆，只测协议链路）

## 验收标准

- 提交里至少有：1 个能渲染的重建场景视频、1 张 SparseDrive 推理可视化、`pytest` 全绿
- `docs/week1_report.md` 记录每日实测延迟、踩坑、回退方案

## 已知阻塞与回退

| 阻塞 | 概率 | 回退 |
|---|---|---|
| DAIR-V2X 审批超 5 天 | 中 | 改 ApolloScape 北京段 |
| CARLA-NuRec 安装失败 | 中 | 单独跑 DriveStudio renderer 模式（不接 CARLA） |
| AlpaSim 不开源 / 不可用 | 中 | 整个 Week 1 不依赖 AlpaSim；Week 3 再决策（含切 SimScale） |
| SparseDrive 推理需 LiDAR 输入分支 | 低 | 用作者的 vision-only 配置；如无，临时切 UniAD |

## Week 2 预告

- AlpaSim 闭环骨架接入（或回退到 SimScale）
- Scenario YAML schema v1
- 第一个完整闭环 demo：dummy reactive agent + DriveStudio renderer + SparseDrive
