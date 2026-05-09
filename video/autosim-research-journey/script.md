>>> 走进森林 #B01
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
全屏深色背景 (#0d1117)。画面垂直居中布局，内容占画布 85%。
[0s] 屏幕中央出现一个渺小的白色像素小人剪影（48px 高），位于画布水平中心，垂直 60% 处。
[0.5s] 小人周围 fade-in 出现一片"森林"——由 12 棵深灰色 (#161b22) 几何化树形 SVG 组成，高度从 80px 到 200px 不等，错落分布在小人左右两侧，整体宽度占画布 80%。
[1.5s] 在小人正上方 80px 处淡入主标题 "AutoSim 调研历程"，字号 110px，粗体，白色 (#e6edf3)。
[2s] 主标题下方 24px 出现 6px 粗 accent (#58a6ff) 横线，从左向右扫入，宽度 70% 主标题宽度。
[2.5s] 横线下方 32px 出现副标题 "一场架构反转记"，字号 56px，颜色 #8b949e。
[3s] 画布底部 80px 处淡入小标签 "13 agents · 4 轮反转 · 6 轮调研 · 0 RED"，字号 28px，#8b949e，居中。

--- narration ---
一个工程师 走进自动驾驶仿真的森林
想造一个能跑 **中国城市** 的闭环测试器
这是他 1 天半 经历的故事


>>> 任务清单 #B02
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部居中 80px 处淡入标题 "用户给的目标"，字号 64px，粗体 #e6edf3。
[0.8s] 标题下 60px 处横向排列 5 张卡片，等距排布，三卡总宽 90% 画布，间距 36px。
每张卡片高 320px，圆角 16px，背景 #161b22，1px 边框 #30363d，内边距 28px：
  ① 🎬 图标 80px，accent 色，标题 "编辑 case" 44px，描述 "场景脚本" 28px #8b949e
  ② 🔄 图标 80px，accent 色，标题 "换算法" 44px，描述 "插拔接口" 28px
  ③ 🎯 图标 80px，accent 色，标题 "测试矩阵" 44px，描述 "case × 算法" 28px
  ④ 🎥 图标 80px，accent 色，标题 "高质量视频" 44px，描述 "可视化输出" 28px
  ⑤ 🌍 图标 80px，accent 色，标题 "sim2world" 44px，描述 "落地真车" 28px
[1.5s] 卡片从左到右依次 slide-up 进入（每张延迟 0.2s）。
[3.5s] 底部 100px 处淡入文字 "听起来 像一个周末项目..."，字号 40px，斜体 italic，#8b949e。

--- narration ---
用户给出 **5 个目标**
编辑 case、换算法、跑 **测试矩阵**
出 **高质量视频**、能 **sim2world** 落地
听起来 像一个周末项目


>>> v1 的乐观 #B03
@enter: fade
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部居中标题 "v1 架构 (上午 10:30)"，字号 56px，#e6edf3，粗体；右侧紧贴"v1"用 accent 色高亮框包裹。
[0.5s] 标题下 50px 出现一张"管道图"占画布 85% 宽度：左中右三个矩形组件，等距排布，间距 60px。
每个矩形高 240px，圆角 16px，背景 #161b22，边框 1px #30363d，内有：
  左：标题 "AlpaSim" 字号 52px 白色，副 "闭环骨架" 32px #8b949e，下方 NVIDIA 绿标签 24px
  中：标题 "NuRec" 52px 白色，副 "神经渲染" 32px，下方 NVIDIA 绿标签
  右：标题 "Cosmos" 52px 白色，副 "世界模型" 32px，下方 NVIDIA 绿标签
[1.5s] 三个组件之间用 4px 粗 accent 色箭头连接，从左到右流向。
[2.5s] 整个管道图下方 60px 出现一行大字 "都是 NVIDIA 主推的"，字号 48px，#e6edf3，居中。
[3s] 大字下方 16px 处出现一行小字 "应该没错吧？"，字号 36px italic，#8b949e。
[4s] 在 "Cosmos" 矩形右上角浮现一个微小的 ❓ 表情符号，accent 色，闪烁。

--- narration ---
第一份方案 30 分钟就画完
**AlpaSim** 做骨架 **NuRec** 做渲染
**Cosmos** 做生成 全是大厂背书
应该 没错吧


>>> 第一刀 #B04
@enter: zoom-in
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 画面正中浮现一个大型终端窗口 SVG，宽度占画布 80%，高度 540px，圆角 16px，背景 #0a0d12，边框 1px #30363d。窗口顶部三个 macOS 风格圆点（红黄绿，14px），左上 16px 处。
[0.5s] 窗口内逐字显示终端命令，等宽字体 28px：
  $ docker pull nvcr.io/nvidia/nre/nre-ga:latest
[1.5s] 命令下方延迟 1s 显示红色 (#ff7b72) 错误：
  Error response from daemon:
  402 Payment Required
[3s] 在终端窗口右上角浮现一个红色感叹号图标 ⚠️ 80px。
[3.5s] 终端窗口下方 40px 处出现解释文字 "NuRec 训练管线与推理服务 = 商业闭源 docker"，字号 38px，#e6edf3，居中。
[4.5s] 该解释文字下 24px 再加一行 "918 个预训练资产 全是欧美 + 不可再分发"，字号 28px，#8b949e。

--- narration ---
但调研第一刀 来得很快
NuRec 训练和推理服务
全部是 **闭源 docker 容器**
论坛上还有人收到 "Payment Required"


>>> 接连两刀 #B05
@enter: slide-left
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 画面分为左右两栏，等宽，间距 48px，整体占画布 90%。
左栏顶部 60px 处标题 "AlpaSim"，字号 60px，粗体白色。下方 32px 出现一张半透明文档卡，高 320px，背景 #161b22，圆角 16px。文档卡上有 5 行模糊文字（用矩形条 #30363d 表示），其中第 3 行被红色 X 划掉，下方一行写 "第三方算法接入 未文档化"，字号 28px，红色 (#ff7b72)。
[1s] 右栏顶部 60px 处标题 "WorldEngine"，字号 60px，粗体白色。下方出现一个圆形进度环 SVG (240px 直径)，蓝色弧线只画了 1/15 圈，环中央显示 "4s"，字号 88px，accent 色；环下方 24px 写 "pseudo-closed-loop demo"，字号 28px，#ff7b72。
[2.5s] 两个栏底部 40px 处共同出现一行大字 "外部独立复现报告：0 条"，字号 44px，#e6edf3，居中跨两栏。
[3.5s] 大字下方 24px 出现 "arXiv 论文：未发布"，字号 32px，#8b949e。

--- narration ---
那 AlpaSim 自己呢
代码开源 但默认 renderer 仅 NuRec
第三方算法接入 **官方未文档化**
WorldEngine 看起来活跃
打开却发现是个 **4 秒 demo**


>>> 关键转折 #B06
@enter: zoom-in
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 画面正中浮现一个聊天气泡 SVG，宽 800px 高 200px，圆角 32px，背景 #161b22，边框 2px accent 色。气泡左上有一个简笔小人头像 64px。
[1s] 气泡内逐字显示文字 "仿真测试可以不用实时"，字号 60px，粗体白色，居中。
[2s] 气泡正上方 60px 出现标签 "用户" 字号 32px，#8b949e。
[2.5s] 在气泡周围 fade-in 出现 6 道 accent 色光线（从气泡向四周辐射），8px 粗，长度 200px，模拟"灵光一现"效果。
[3.5s] 画面底部 80px 处淡入大字 "整个架构 瞬间豁然开朗"，字号 56px，accent 色，粗体居中。
[5s] 大字下方 16px 处出现小字 "latency 不再是死结 → Cosmos / VLM / 慢渲染全部可用"，字号 28px，#8b949e。

--- narration ---
在快要放弃的时候
用户补了一句话
**"仿真不需要实时"**
整个架构 瞬间豁然开朗


>>> 标准答案早就存在 #B07
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 画面中央出现一个巨型路标 SVG，木牌样式，宽 720px 高 200px，背景 #58a6ff (accent)，圆角 8px，箭头朝右。
[1s] 路标上逐字写出 "NAVSIM v2"，字号 96px，白色，粗体，等宽字体。
[2s] 路标下方 60px 出现 3 个数据气泡，横向等距，总宽 80% 画布：
  ① 圆形气泡 200px，背景 #161b22 边框 accent，内字 "12k" 字号 72px accent 色，下方 24px 标签 "navtest cases" 字号 24px #8b949e
  ② 圆形气泡 200px，内字 "EPDMS" 字号 56px accent，下方标签 "标准 metric"
  ③ 圆形气泡 200px，内字 "SOTA ↑" 字号 72px accent，下方标签 "全在这刷榜"
[4s] 最底部 80px 出现 "2026 年的事实标准"，字号 44px，#e6edf3 居中。

--- narration ---
离线批跑的 **标准答案** 早就存在
它叫 **NAVSIM v2**
自带 12000 个 case 和 EPDMS 报告
2026 年所有 SOTA 都在它上面刷榜


>>> 四国演义 #B08
@enter: fade
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部居中标题 "渲染层 不必二选一"，字号 56px，#e6edf3 粗体，距顶 80px。
[0.8s] 标题下方 60px 处横向排列 4 个等宽矩形 panel，间距 32px，总宽占画布 92%，每个矩形高 380px，圆角 16px，背景 #161b22 边框 1px #30363d，内边距 24px：
  ① 顶部小标签 "Track A1" accent 色 24px，中间大字 "CARLA UE4" 48px 白色粗体，下方描述 "几何 baseline" 28px #8b949e，底部 emoji 🎯 60px
  ② "Track A2" / "CARLA UE5" / "视觉升级" / 🎨
  ③ "Track B" / "Cosmos" / "生成中国感" / 🌏
  ④ "Track C" / "gsplat 重建" / "真照片对照" / 📷
[2s] 4 panel 依次 slide-up 进入，每个延迟 0.3s。
[4s] panel 下方 60px 出现一行大字 "同一个 case · 4 种渲染 · 1 张报告"，字号 48px，accent 色居中。

--- narration ---
渲染层 不必二选一
让 **CARLA**、**Cosmos**、**3DGS 重建** 三路并行
用户还想看 UE5 那就再加一路
**同一个 case 4 种渲染 1 张报告**


>>> 最后的暗礁 #B09
@enter: slide-left
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 画面中央出现一个日历 SVG，宽 600px 高 480px，背景 #161b22 圆角 16px 边框 1px #30363d。日历表格 3×4 网格表示 12 个月，每个格子 140px×100px。
[1s] 从 2024-12 格子开始（左上角），格内显示 "v0.10 release" 字号 24px accent 色。其后 17 个格子全部填充 "—" 字号 32px #ff7b72，表示 17 月无 patch。
[2.5s] 日历右上角浮现一个红色感叹号 ⚠️ 80px。
[3s] 日历下方 50px 出现两行大字：
  第 1 行 "CARLA 0.10 = 17 个月无 patch"，字号 44px #e6edf3
  第 2 行 "Bench2Drive 仍锁 0.9.15" 字号 36px #8b949e
[4.5s] 最底部出现结论 "**主线 0.9.16 · 副线 0.10**"，字号 48px accent 色 粗体，居中。

--- narration ---
最后一轮 落地核查
发现 CARLA 0.10 已经 17 个月没动过
Bench2Drive 还锁在 **0.9.15**
**主线必须 0.9.16** 副线才放 0.10


>>> 终极架构 #B10
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部居中标题 "v4-final"，字号 96px accent 色 粗体，距顶 60px。下方 16px 出现 6px 粗 accent 横线（宽 280px）。
[1s] 横线下 50px 出现一张管道图占画布 92%：
  上层一个长条矩形 "OSC 2.0 Case → CARLA Synchronous" 高 100px 宽 80% 画布，标签 36px 居中
  下方分支为 4 条平行轨道 (4 panel 横排，间距 32px)：
    A1=UE4 / A2=UE5 / B=Cosmos / C=gsplat
    每个 panel 高 180px 宽相等，背景 #161b22，标签 32px 白色
  4 轨下方汇合到一个矩形 "E2E 算法 + 自行车模型 + 闭环回灌"，高 100px 宽 80%
  最底部一个矩形 "EPDMS 测试报告（4 轨 × N 算法）"，高 100px 宽 60%，accent 色边框
  矩形之间用 4px 粗 accent 色箭头连接。
[3.5s] 画面右上角浮现 4 个标签纵向排列：
  "0 RED 阻断" 28px 绿色 (#3fb950)
  "8 决策锁定" 28px accent
  "13 agents 调研" 28px #8b949e
  "4 轮反转" 28px #8b949e

--- narration ---
经过 **6 轮调研** 和 **4 轮反转**
v4-final 架构终于锁定
**8 个决策 4 条渲染轨道**
**0 个 RED 阻断**


>>> 经验教训 #B11
@enter: fade-up
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 顶部居中标题 "如果重来 早问 5 个问题"，字号 60px #e6edf3 粗体。
[0.8s] 标题下方 50px 处出现一个垂直列表，整体居中，宽 70% 画布，每行高 80px：
  Q1 "**实时性？**"  标签 "影响渲染 + IPC"   字号 44px / 28px
  Q2 "**商用还是自研？**"  "影响许可证 + 出口管制"
  Q3 "**数据必须中国吗？**"  "决定 MVP 数据"
  Q4 "**闭环深度多深？**"  "4s pseudo / 30s 慢跑 / 实时"
  Q5 "**要不要可视化对外？**"  "决定是否上 Cosmos"
每行左侧用一个小圆形序号 (48px accent 色)，序号后跟问题（白色 44px 粗体），右侧灰色注解 28px。
[3s] 列表底部 60px 处出现总结 "这 5 个问题 决定整个架构的形状"，字号 40px，accent 色，居中。

--- narration ---
最大的教训其实是
**早问 5 个问题**
实时性 商用 数据 闭环深度 可视化
这 决定整个架构的形状


>>> 出发 #B12
@enter: zoom-in
@exit: fade
@visual: animation

--- visual ---
深色背景 (#0d1117)。
[0s] 画面正中出现 B01 那个像素小人剪影（同样 48px 高），但这次他站在画布右下方，朝向画面右侧。小人正前方画一条 6px 粗 accent 色虚线箭头，从小人位置向右上方 45° 角延伸到画布外。
[1s] 画面正上方 100px 处淡入大字 "Phase 1 已就绪"，字号 96px 白色 粗体居中。
[2s] 大字下方 32px 出现副标题 "5 个 hello-world · 1 份测试报告 · 一个新起点"，字号 36px #8b949e 居中。
[3s] 画面右下角小人右上方 200px 处出现"目的地" SVG——一个 88px 直径的圆形旗帜图标，accent 色，旗杆 #e6edf3。
[4s] 画面底部 80px 处淡入文字 "下次见 我们带回真车数据"，字号 32px italic accent 色 居中。

--- narration ---
Phase 1 已就绪
5 个 hello-world 验证
第一份 EPDMS 测试报告
**下次见** 我们带回 **真车数据**
