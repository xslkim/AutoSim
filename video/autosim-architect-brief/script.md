>>> 项目定位 #B01
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。整体内容占画布 85%。
[0s] 顶部居中 80px 处淡入主标题 "AutoSim 架构简报"，字号 110px 粗体白色 (#e6edf3)。
[0.8s] 主标题正下方 24px 处出现 6px 粗 accent (#58a6ff) 横线，宽度 = 主标题宽度的 70%，从左向右扫入。
[1.5s] 横线下方 28px 出现副标题 "Pure-Vision E2E AD Closed-Loop Simulator · v4-final"，字号 44px，颜色 #8b949e，字母间距正常。
[2.5s] 画面下半部居中位置出现 4 个约束 chip，横向等距排列，总宽占画布 80%，间距 24px。每 chip 高 100px 圆角 50px 背景 #161b22 边框 1px #30363d，内部居中文字 36px 白色：
  ① 🇨🇳 中国城市
  ② ☁️ 算力上云
  ③ 📊 公开数据
  ④ 🔬 自研非商用
[3.5s] 4 chip 依次淡入（每个延迟 0.2s）。
[5s] 画布最底部 60px 处淡入小字 "2026-05-09 · 13 agents 调研 · 4 轮反转 · 0 RED"，字号 24px，颜色 #8b949e，居中。

--- narration ---
项目目标 纯视觉端到端 自动驾驶闭环仿真器
场景 **中国城市** 离线批跑 出测试报告
性质 自研非商用 算力上云 公开数据
约束已定 进入设计


>>> 设计原则 #B02
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部居中 80px 处标题 "设计原则"，字号 64px 粗体白色。
[0.8s] 标题下方 50px 处出现 2×2 网格，整体占画布 80% 宽度 70% 高度，单元格间距 36px。每个单元格圆角 16px 背景 #161b22 边框 1px #30363d 内边距 36px：
  左上 ①: 顶部数字 "01" accent 色 字号 44px 等宽 / 标题 "三层解耦" 56px 粗体白色 / 描述 "case · renderer · 算法 完全独立" 28px #8b949e
  右上 ②: "02" / "采用社区标准" / "NAVSIM v2 · OSC 2.0 · gsplat 不造轮子"
  左下 ③: "03" / "多 renderer 对照" / "4 轨同 case 同算法 横向比对"
  右下 ④: "04" / "死胡同明确退出" / "退出原因带证据 不重复探索"
[2s] 4 个单元格依次 zoom-in 进入（左上→右上→左下→右下，每个延迟 0.3s）。

--- narration ---
四条原则 贯穿整个架构
**三层解耦** case 渲染 算法各自独立
**社区标准优先** NAVSIM v2 OSC 2.0 直接采纳
**多 renderer 对照** 避免单点失败
死胡同必须 **带证据退出**


>>> 架构总览 #B03
@enter: fade
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 处标题 "Pipeline 总览" 字号 56px 粗体白色。
[0.8s] 标题下方 40px 出现完整管道图，整体占画布 90% 宽度。从上到下分 5 层，每层之间用 4px 粗 accent 色箭头垂直连接：
  Layer 1 (高 90px 宽 70% 居中): 矩形 #161b22 边框 1px #30363d，内字 "OSC 2.0 case · ScenarioRunner" 字号 36px 白色
  Layer 2 (高 90px 宽 70% 居中): 矩形 #161b22，内字 "CARLA 0.9.16 同步模式 · --RenderOffScreen" 字号 36px 白色
  Layer 2 右侧浮出标注 "→ {HDMap, ego, agents, weather, t}" 字号 24px italic accent 色
  Layer 3: 4 个并排矩形（高 140px 等宽，间距 24px，总宽 92% 画布）：
    A1 "CARLA UE4" + 副 "几何 baseline" 32px+24px
    A2 "CARLA UE5" + "视觉升级"
    B "Cosmos+LoRA" + "中国感生成"
    C "gsplat 重建" + "真照片对照"
    每个矩形顶部带一个色标 (A1=蓝, A2=紫, B=橙, C=绿)，4px 厚
  Layer 4 (高 90px 宽 70% 居中): 矩形 accent 色边框 2px，内字 "E2E 算法 (Plugin Protocol) · SparseDriveV2 / Senna" 36px 白色
  Layer 5 (高 90px 宽 50% 居中): 矩形 accent 色填充 (#1f4068)，内字 "EPDMS 报告 · 4 轨 × N 算法" 36px 白色粗体
[3s] 整图 fade-in 完成；最右侧追加一条粉色虚线箭头 (从 Layer 5 弯回 Layer 2，accent 色 dashed 4px)，标签 "闭环回灌" 28px italic accent 色。

--- narration ---
顶层 OSC 2.0 描述 case
CARLA 同步模式 跑物理和反应式 agent
**四 renderer 并列** 接收同一 state
E2E 算法消费像素 输出轨迹回灌


>>> 决策 D1–D4 #B04
@enter: slide-left
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 处标题 "决策表 (1/2) · D1–D4"，字号 52px 粗体白色。
[0.8s] 标题下方 40px 处出现一个 4 行表格，整体占画布 88%。表头一行 (高 60px) 背景 #1f2937，列宽分别 12% / 25% / 50% / 13%：
  列名: "ID" / "决策项" / "选定" / "评级"
  表头字号 32px 粗体 accent 色
[1.5s] 表格 4 行依次出现（每行延迟 0.4s），行高 110px 交替背景 #161b22 / #1a1f29，单元格内边距 24px：
  D1 / 闭环骨架 / **CARLA 0.9.16 主 + 0.10 副** / 🟡
  D2 / MVP 算法 / **SparseDriveV2 主 + Senna 副** / 🟢/🟡
  D3 / 首个数据 / **nuScenes mini + ApolloScape + DrivingDojo** / 🟢
  D4 / 渲染层 / **A1=UE4 / A2=UE5 / B=Cosmos / C=gsplat** / 🟢
  ID 列字号 36px accent 色等宽；决策项列 32px 白色；选定列 30px 白色（粗体词高亮 accent 色）；评级列 36px 居中。

--- narration ---
**D1** 骨架 CARLA 0.9.16 主 0.10 副
**D2** 算法 SparseDriveV2 主 Senna 副
**D3** 数据 nuScenes mini 起步
**D4** 渲染 四轨道 A1 A2 B C 并列


>>> 决策 D5–D8 #B05
@enter: slide-left
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 处标题 "决策表 (2/2) · D5–D8"，字号 52px 粗体白色。
[0.8s] 同样 4 行表格，结构同 B04，表头列宽相同：
  D5 / case 编辑 / **OpenSCENARIO 2.0 + ScenarioRunner** / 🟡
  D6 / 渲染路由 / **Python ABC (无 gRPC)** / 🟢
  D7 / 评测脚手架 / **NAVSIM v2 metric + Scene pickle adapter** / 🟡
  D8 / 阶段策略 / **Phase 1 单轨 → 四轨 → 真闭环** / 🟢
[3s] 表格右下角浮出小字 "🟢 GREEN · 🟡 YELLOW · 🔴 RED · 0 RED 阻断"，字号 26px #8b949e。

--- narration ---
**D5** case 编辑 OpenSCENARIO 2.0
**D6** 路由 Python ABC 离线无需 gRPC
**D7** 评测 NAVSIM v2 metric 库
**D8** 阶段 单轨到四轨到真闭环


>>> Plugin Protocol #B06
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 处标题 "E2E 算法插件接口"，字号 52px 粗体白色。下方 12px 一行小字 "src/autosim/e2e_plugins/protocol.py" 字号 28px italic #8b949e 等宽字体居中。
[0.8s] 中央出现一个代码块面板，宽度 80% 画布，高度 540px，背景 #0a0d12 圆角 16px 边框 1px #30363d 内边距 32px。代码块顶部三个 macOS 圆点 (14px) 左上 16px。代码用等宽字体 30px，关键字色 #ff7b72，字符串色 #a5d6ff，注释色 #8b949e，常规色 #e6edf3。代码内容（每行从上到下逐字 typewriter 出现，0.5s 间隔）：
```
class E2EPlanner(Protocol):
    def reset(scenario_meta) -> None
    def step(obs: Observation) -> Action
    def close() -> None

# Observation: images, ego_state, nav_command, ...
# Action:      trajectory K×3 (x, y, heading)
```
[5s] 代码块下方 32px 出现两行注解：
  第 1 行 "仿真器只消费 trajectory" 字号 36px 白色
  第 2 行 "由自行车模型跟踪 → 与算法完全解耦" 字号 30px #8b949e

--- narration ---
插件接口 跨 v1 到 v4-final 没改过
输入 多相机图像 + ego state + 导航
输出 K×3 轨迹 仅此而已
**仿真器只看轨迹** 与算法彻底解耦


>>> 四 renderer 设计意图 #B07
@enter: fade
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 处标题 "四 renderer 各司其职"，字号 52px 粗体白色。
[0.8s] 标题下方 40px 横向 4 panel 排列，间距 24px 总宽 92%。每个 panel 高 480px 圆角 16px 内边距 28px 背景 #161b22 顶部一条 4px 厚色标：
  Panel 1 色标蓝色: 顶部 chip "Track A1" 24px / 标题 "CARLA UE4" 48px 粗体白色 / 用途 "Bench2Drive 220 case 兼容 几何 GT" 28px #8b949e / 底部图标 🎯 80px / 评级 🟢
  Panel 2 色标紫色: chip "Track A2" / "CARLA UE5" / "视觉升级实验 dead branch 风险已知" / 🎨 / 🟡
  Panel 3 色标橙色: "Track B" / "Cosmos + LoRA" / "中国感生成 case 编辑灵活 高质量视频" / 🌏 / 🟢
  Panel 4 色标绿色: "Track C" / "gsplat 3DGUT" / "真照片重建 sim2real 黄金对照" / 📷 / 🟢
[3s] 4 panel 下方 60px 处出现一行大字 "同 case · 同算法 · 4 套 EPDMS 报告 → 跨渲染域鲁棒性"，字号 36px accent 色 居中。

--- narration ---
四个 renderer 各有所长
A1 几何 baseline 算法 GT 算这条
A2 UE5 视觉升级 实验性
B Cosmos 出 **中国感** 和高质量视频
C gsplat 重建 **sim2real 黄金对照**


>>> 数据策略 #B08
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 标题 "数据策略 · 避审批"，字号 52px 粗体白色。
[0.8s] 中央出现一个 2 列 5 行的对比表格，宽 80% 画布。表头高 56px 背景 #1f2937 字号 30px accent 色：
  列 1 "数据集" 25%；列 2 "可用性" 30%；列 3 "用途" 30%；列 4 "评级" 15%
[1.5s] 5 行依次出现 (每行高 80px 交替背景 #161b22 / #1a1f29 字号 28px)：
  ✅ nuScenes mini / 直接下载 ~3GB / MVP 验证管线 / 🟢
  ✅ DrivingDojo (HF) / 自动条款 283GB / 世界模型 FT / 🟢
  ✅ ApolloScape 北京 / GitHub 开放 / 中国风格补充 / 🟢
  📧 ONCE / 申请页 1 年未更新 / Phase 2 中国扩展 / 🟡
  📧 DAIR-V2X-V / dair@air.tsinghua / V2X 专用 + 22k 帧 / 🟢
[3.5s] 表格下方 40px 处出现两行：
  第 1 行 "Phase 1 不依赖任何待审批数据" 字号 36px accent 色 居中粗体
  第 2 行 "并行启动 ONCE / DAIR-V2X 申请 不阻塞主线" 字号 28px #8b949e 居中

--- narration ---
MVP 必须 **免审批** 起步
nuScenes mini DrivingDojo ApolloScape 直接可用
ONCE 和 DAIR-V2X 全集 **并行申请**
Phase 1 不依赖任何待审批数据


>>> 风险登记册 #B09
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 标题 "风险登记册 · 14 项"，字号 52px 粗体白色。
[0.8s] 中央偏上 出现 3 个统计卡片横向排列 间距 32px 总宽 80%：
  卡片 1 高 200px 圆角 16px 背景 #161b22 边框 1px #30363d：顶部 "0" 字号 120px 粗体 #3fb950 (绿色) / 下方 "RED 阻断" 32px 白色
  卡片 2: "2" 120px accent 色 / "YELLOW 已识别+缓解" 32px
  卡片 3: "12" 120px #8b949e / "次要风险 计入 Phase 1" 32px
[2.5s] 卡片下方 50px 处列出两个关键 YELLOW 详情 (左右两列 间距 32px 各占 40% 画布)：
  左列: 顶部小标签 "YELLOW #1" accent 24px / 标题 "CARLA 0.10 dead branch" 36px 白色 / 缓解 "A2 仅作实验副线 0.9.16 主线" 24px #8b949e
  右列: "YELLOW #2" / "Senna 无 NAVSIM 数字" / "自建 harness ~1 周 计入 Week 2"
[5s] 画面底部 50px 处文字 "所有风险来源 + 缓解方案见 docs/architecture.md §5"，字号 24px italic #8b949e 居中。

--- narration ---
14 项已识别风险
**0 个 RED 阻断**
2 个 YELLOW 已识别 + 已有缓解
12 个次要风险 计入 Phase 1 计划


>>> 阶段策略 #B10
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部 60px 标题 "阶段策略 · 风险递增 产出递增"，字号 50px 粗体白色。
[0.8s] 标题下方 50px 处一条水平时间轴 (粗 4px accent 色) 占画布 85% 宽度，左右各留 7.5% padding。轴上 3 个节点圆点 (直径 32px accent 色) 等距分布。每个节点上方 60px 处 panel (高 280px 宽 28% 画布 圆角 16px 背景 #161b22 内边距 24px)：
  Panel 1 (Phase 1): 顶 "Phase 1" 32px accent / 标题 "MVP 单轨" 40px 白色粗体 / 内容 ① "CARLA 0.9.16 + nuScenes mini" / ② "SparseDriveV2 接入" / ③ "第一份 EPDMS 报告" 字号 24px #8b949e
  Panel 2 (Phase 2): "Phase 2" / "四轨对照" / ① "A1+A2+B+C 并行" / ② "Senna NAVSIM harness" / ③ "中国 case 库 100 条"
  Panel 3 (Phase 3): "Phase 3" / "真闭环 + 量产" / ① "HUGSIM 真闭环" / ② "ReconDreamer++ off-traj" / ③ "ONCE 中国数据扩展"
[2.5s] 时间轴下方每个节点下 24px 处出现周数标签 "W1–W6" / "W7–W12" / "W13+" 字号 28px accent 色等宽居中。

--- narration ---
**Phase 1** 单轨 + nuScenes mini 出第一份报告
**Phase 2** 四轨对照 + 中国数据 + Senna
**Phase 3** HUGSIM 真闭环 + 中国 case 库
风险递增 产出递增


>>> 状态 #B11
@enter: zoom-in
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 画面正上方 100px 处淡入大字 "v4-final · 方向锁定"，字号 88px 粗体白色 居中。
[1s] 标题下方 16px 处出现 6px 粗 accent 色横线 (宽 320px) 从中心向两侧扫开。
[1.5s] 横线下方 50px 处一个 2×3 状态网格 占画布 70% 宽度 间距 24px。每个单元格高 100px 圆角 12px 背景 #161b22 内边距 24px 横向 flex (左侧大型对勾图标 60px 绿色 (#3fb950)，右侧上下两行文字)：
  ✓ "13 agents 调研" 28px / "完成" 22px #8b949e
  ✓ "4 轮架构反转" 28px / "收敛"
  ✓ "2 轮落地核查" 28px / "完成"
  ✓ "0 RED 阻断" 28px / "确认"
  ✓ "8 决策锁定" 28px / "记录"
  ✓ "6 份文档落地" 28px / "可执行"
[4s] 状态网格下方 50px 处淡入文字 "下一步 · Phase 1 · D0 数据申请 + D1 项目骨架"，字号 36px accent 色 粗体 居中。

--- narration ---
v4-final **方向锁定**
13 agents 调研完成 0 RED 阻断
8 决策落地 6 份文档可执行
下一步 **Phase 1 D0** 启动数据申请
