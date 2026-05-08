# AutoSim

纯视觉端到端自动驾驶闭环仿真器。中国城市，运动学车辆，sim2real 落地。

## 状态

阶段 2（架构 PoC）— 2026-05-08。仓库刚启动，尚无可运行代码。

## 三个已锁定决策

1. **闭环骨架** — NVIDIA AlpaSim 为主，OpenDriveLab SimScale 作反应式 agent 补充。
2. **首个端到端算法** — SparseDrive（9 FPS、稀疏 query 易调试）。后续接入 Hydra-NeXt、DiffusionDrive、UniAD、DriveTransformer 做横评。
3. **首个数据集** — DAIR-V2X 北京路口（数据量小、V2X 已校准、闭环最易跑通）。MVP 跑通后扩到 ONCE 多城。

## 文档

- [架构](docs/architecture.md)
- [Week 1 任务](docs/week1_plan.md)

## 技术栈一览

| 层 | 选型 |
|---|---|
| 闭环骨架 | AlpaSim + SimScale |
| 几何/渲染 | NuRec（CARLA 集成）+ DriveStudio/OmniRe |
| Off-trajectory 修复 | ReconDreamer++ + DriveX |
| 世界模型 | Cosmos-Predict2.5-2B |
| E2E 算法 | SparseDrive（MVP）→ Hydra-NeXt / DiffusionDrive / UniAD / DriveTransformer |
| 车辆运动学 | 自行车模型 + Pure Pursuit/LQR |
| 中国数据 | DAIR-V2X（MVP）→ ONCE + ApolloScape；DrivingDojo 用于世界模型 FT |
| Benchmark | Bench2Drive、NAVSIM v2、DriveArena、HUGSIM |
