# AI Agent 安装与下载任务清单（v4-final · Phase 1 W1）

> **读者：AI agent**。
> **目标**：把项目所需的全部代码仓库、Python 库、容器镜像、模型权重、数据集**下载并安装到位**。
> **非目标**：本任务**不要求运行**任何训练/推理/CARLA 启动；只验证"装好且可见"。
> **目标机器**：云上 H100 / V800 80G 单机（Linux x86_64）。本地 Windows 开发机不是部署目标，不要在 Windows 上装 CARLA。
> **决策来源**：[architecture.md](architecture.md) D1–D8、[milestone_1_plan.md](milestone_1_plan.md)。如本文与之冲突，以 architecture.md 为准。

---

## 0. 全局约束（agent 必读）

1. **禁止运行**：不启动 CARLA、不开始训练、不跑推理。只下载/安装/编译，最多做 `import` smoke test。
2. **禁止改方向**：D1–D8 已锁定，不要替换 SparseDriveV2、不要换 CARLA 版本、不要选别的 Cosmos 变体。如发现安装阻塞，**记录到 `docs/install_report.md` 并停下**等用户决策，不要自行换方案。
3. **失败可恢复**：每一节末尾给了 fallback。允许跳过非阻塞项（标记 `[OPTIONAL]`），必须完成的项标记 `[BLOCKING]`。
4. **磁盘预算**：总下载量约 **~280 GB**（CARLA 镜像 ~30G + Cosmos-Predict2.5-2B ~32G + Cosmos-Drive-Dreams-7B ~28G + nuScenes mini ~3G + ApolloScape 北京段 ~50G + DrivingDojo HF ~100G + 其他权重 ~30G）。安装前 `df -h` 确认 `/data` 至少有 450 GB 余量。
5. **网络**：如 HuggingFace / GitHub 慢，使用 `HF_ENDPOINT=https://hf-mirror.com` 与 GitHub 代理；不要为了"省事"换镜像源里的不同模型。
6. **凭证**：HuggingFace token、Google Drive、ONCE / DAIR-V2X 邮箱审批等需要用户操作的环节，agent 应**生成清单交给用户**，不要尝试自己注册账号。
7. **进度记录**：每完成一节，向 `docs/install_report.md` 追加：节号、命令、产物路径、磁盘占用、耗时、md5（如适用）。

---

## 1. 系统与 Python 环境 [BLOCKING]

### 1.1 系统侧
- OS: Ubuntu 22.04（CARLA 0.9.16 / 0.10 官方支持）
- NVIDIA Driver ≥ 535
- CUDA Toolkit 12.1（与 PyTorch 2.4 匹配）
- Docker ≥ 24 + nvidia-container-toolkit
- git, git-lfs, build-essential, cmake, ffmpeg

### 1.2 Conda env
```bash
conda create -n autosim python=3.10 -y
conda activate autosim
# PyTorch 2.4 + CUDA 12.1
pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
```

### 1.3 项目骨架与开发工具
- 在仓库根创建 `environment.yml` 和 `requirements.txt`（先空文件占位，由本任务逐节追加）
- `pip install ruff pyright pytest mypy`
- 不要执行 `src/autosim/` 包骨架创建（那是 Day 1 的开发任务，不属于安装范围）

**验证**：`python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"` 必须输出 `True 12.1`。

---

## 2. CARLA 容器镜像 [BLOCKING]

> 不要 from-source 编译 UE4/UE5，**只拉官方 docker image**。

```bash
docker pull carlasim/carla:0.9.16          # A1 主轨道
docker pull carlasim/carla:0.10.0          # A2 副轨道（实验视觉）
docker pull carlasim/carla:0.9.15          # 备份，给 Bench2Drive 兼容（可选）
```

**验证**：`docker images | grep carla` 列出三个 image，每个约 8–12 GB。**不要 `docker run`**。

**Fallback**：如 0.10 拉取失败或镜像损坏 → 仅记录、跳过，A2 在 W1 hello-world 阶段会单独验证退场（见 R11）。

---

## 3. ScenarioRunner + Bench2Drive [BLOCKING]

```bash
mkdir -p third_party && cd third_party
git submodule add https://github.com/carla-simulator/scenario_runner.git
git submodule add https://github.com/Thinklab-SJTU/Bench2Drive.git
cd scenario_runner && pip install -r requirements.txt && cd ..
```

**注意**：ScenarioRunner 的 OSC 2.0 解析依赖 `carla` Python 客户端 wheel（pip 包，不是 docker 内的）：
```bash
pip install carla==0.9.16
```

**Fallback**：如 `pip install carla==0.9.16` 在 H100 失败（已知有版本与 wheel 平台兼容问题），从 docker 容器里把 `PythonAPI/carla/dist/*.whl` 拷出来本地装。

---

## 4. E2E 算法仓库与权重 [BLOCKING]

### 4.1 SparseDriveV2（MVP 主，D2）
```bash
cd third_party
git submodule add https://github.com/swc-17/SparseDriveV2.git
cd SparseDriveV2 && pip install -r requirements.txt && cd ../..
```
- 权重：ResNet-34 ImageNet pretrained（仓库 README 指定 URL，~85 MB），下载到 `third_party/SparseDriveV2/ckpt/`
- 不要尝试自己训练 NAVSIM v2 权重；MVP 先跑作者发布权重（如有），否则记录到 install_report 等用户决策。

### 4.2 Senna（MVP 副，D2）
```bash
cd third_party
git submodule add https://github.com/hustvl/Senna.git
cd Senna && pip install -r requirements.txt && cd ../..
```
- HF 权重：`rb93dett/Senna`（约 14 GB，含 vision encoder + LLM head）
- 依赖基座：
  - `lmsys/vicuna-7b-v1.5`（~13 GB）
  - `liuhaotian/llava-v1.6-vicuna-7b`（~14 GB，仅数据生成依赖；如显存吃紧可推迟，记到 W2）
- HF 下载用 `huggingface-cli download <repo_id> --local-dir <path>`，不要用 `snapshot_download` 写脚本。

### 4.3 横评算法 [OPTIONAL]（W3+ 才用，先克隆但不装依赖）
仅 `git submodule add` 不 `pip install`：
- `https://github.com/woxihuanjiangguo/Hydra-NeXt` （或最新官方 fork）
- `https://github.com/hustvl/DiffusionDrive`
- `https://github.com/OpenDriveLab/DriveLM`
- `https://github.com/taco-group/OpenEMMA`

---

## 5. 渲染层依赖 [BLOCKING]

### 5.1 gsplat（Track C 核心）
```bash
pip install gsplat>=1.5.0
```
- 这一步会触发 CUDA kernel 编译，**确保 nvcc 可见且与 torch CUDA 12.1 一致**。
- 编译失败的常见原因：`gcc` 版本过新（>13）→ 装 `gcc-11` 并 `export CC=gcc-11 CXX=g++-11`。

### 5.2 DriveStudio（Track C 训练入口）
```bash
cd third_party
git submodule add https://github.com/ziyc/drivestudio.git
cd drivestudio && pip install -r requirements.txt && cd ../..
```
- 不要执行 `examples/simple_trainer.py`（那是 Day 3 hello-world）。

### 5.3 Mip-NeRF360 garden（gsplat 编译验证集，~600 MB）[OPTIONAL]
仅下载到 `data/external/mipnerf360_garden/`，W1 Day 3 才会用上。

### 5.4 Cosmos（Track B 核心）
见第 6 节，单列。

---

## 6. Cosmos：模型谱系与双模型策略 [BLOCKING]

### 6.1 Cosmos 模型谱系（NVIDIA World Foundation Models）

| 子族 | 模型 | 任务 | 参数量 | 本项目用途 |
|---|---|---|---|---|
| Predict1 | Cosmos-1.0-Diffusion-7B/14B (Text2World/Video2World) | 视频生成 | 7B / 14B | ❌ 上代，已被 2.5 取代 |
| Predict1 | Cosmos-1.0-Autoregressive-4B/12B | 视频生成（AR） | 4B / 12B | ❌ 同上 |
| Predict2 | Cosmos-Predict2-2B/14B (Text2Image, Video2World) | 图像 + 视频 | 2B / 14B | ⚠️ 已被 2.5 统一覆盖 |
| **Predict2.5** | **Cosmos-Predict2.5-2B** | **多视角视频生成（Text/Image/Video → World）** | **2B** | ✅ **Track B backend #1：通用基座 + DrivingDojo LoRA → 中国感** |
| Predict2.5 | Cosmos-Predict2.5-14B | 同上 | 14B | ❌ 太重，串行跑也吃力 |
| Transfer | Cosmos-Transfer1-7B | sim → real 风格迁移（depth/seg/edge 控制） | 7B | ❌ Drive-Dreams 已 post-trained，无需直用 Transfer |
| **Drive-Dreams** | **Cosmos-Drive-Dreams-7B (Transfer1 后训练，Sample-AV-Multi-View)** | **HD map + 3D bbox + ego traj → 多视角驾驶视频** | **7B** | ✅ **Track B backend #2：AV 高质量 baseline，无中国感 LoRA** |
| Reason | Cosmos-Reason1-7B | 场景 VLM 推理 | 7B | ❌ 与 Senna 角色重叠 |
| Tokenizer | Cosmos-Tokenizer | 视频分词器（被上面模型内部用） | — | 🔧 自动随权重拉取 |

### 6.2 双模型策略（Track B 内部，**串行运行不并行**）

Track B 单一渲染轨道 + 两个可切换 backend，每次跑同一 case 时只挂一个，**避免显存冲突**：

| Backend | 模型 | 输入条件 | 强项 | 角色 |
|---|---|---|---|---|
| **B-cn** | Predict2.5-2B + DrivingDojo LoRA | text / image | 中国城市风格 | D4 原计划，主报告用 |
| **B-av** | Drive-Dreams-7B | HD map + 3D bbox + ego traj | AV 多视角真实感（北美先验）| 高质量基座对照，AV-domain sanity |

**串行编排**（Phase 2 评测脚手架，写在 `scripts/run_closed_loop.py` 里）：
```
for case in cases:
    for backend in [B-cn, B-av]:        # 串行：一次只载入一个，跑完卸载
        renderer = make_cosmos_renderer(backend)
        run_closed_loop(case, renderer)  # CARLA → renderer → SparseDriveV2 → control
        renderer.unload()                # 释放显存，让下一个 backend 装载
```

**为什么不双子轨并行**（用户已确认）：
- 离线批跑无延迟约束，串行跑两遍只是时间成本翻倍，没必要并行占双倍显存
- 显存预算更宽裕：单 backend 时仍能在同一张卡上挂 CARLA + SparseDriveV2
- 评测层面：同 case × 两 backend 的 EPDMS 已经能给出对照（不需要同步同帧）

**为什么仍保留两个 backend、不二选一**：
- B-cn（Predict2.5+LoRA）回答："我们的中国感 LoRA 是否有用？"
- B-av（Drive-Dreams）回答："如果直接用业界最强 AV 视频基座（无中国感），E2E 算法表现如何？"
- 这是 v4-final"四轨道一致性"独创点的自然延伸，paper 角度有价值

### 6.3 下载步骤（**只下载，不推理**）

#### 6.3.1 Cosmos-Predict2.5-2B（B-cn 基座）
```bash
huggingface-cli login                    # 用户执行
# 用户在网页接受 OML 协议：
#   https://huggingface.co/nvidia/Cosmos-Predict2.5-2B  →  Agree

HF_ENDPOINT=https://hf-mirror.com \
huggingface-cli download nvidia/Cosmos-Predict2.5-2B \
  --local-dir models/cosmos-predict2.5-2b \
  --local-dir-use-symlinks False

cd third_party
git clone https://github.com/nvidia-cosmos/cosmos-predict2.5.git
cd cosmos-predict2.5 && pip install -e . && cd ../..
```

#### 6.3.2 Cosmos-Drive-Dreams-7B（B-av 直出）
```bash
# OML 协议同样需要用户在网页接受：
#   https://huggingface.co/nvidia/Cosmos-Drive-Dreams-7B  →  Agree
# （NV 也发布了 Sample-AV-Multi-View 后训练版本，本项目选 multi-view 版以对齐 6/7 cam 输出）

HF_ENDPOINT=https://hf-mirror.com \
huggingface-cli download nvidia/Cosmos-Drive-Dreams-7B \
  --local-dir models/cosmos-drive-dreams-7b \
  --local-dir-use-symlinks False

# 推理库：Drive-Dreams 走 cosmos-transfer1 推理栈（不是 cosmos-predict2.5）
cd third_party
git clone https://github.com/nvidia-cosmos/cosmos-transfer1.git
cd cosmos-transfer1 && pip install -e . && cd ../..

# 配套样例 / 工具仓（HD map + bbox conditioning 转换器）
cd third_party
git clone https://github.com/nv-tlabs/Cosmos-Drive-Dreams.git
cd Cosmos-Drive-Dreams && pip install -r requirements.txt && cd ../..
```

> **注意**：Drive-Dreams 与 Predict2.5 的 Python 依赖可能有版本冲突（diffusers / transformers / xformers 版本不同）。如冲突，**装两个独立 conda env**：`autosim`（主，含 Predict2.5）+ `autosim-drive-dreams`（仅含 Drive-Dreams 推理栈）。串行跑时切 env，不要试图在同一 env 里强解。

#### 6.3.3 共享 tokenizer（自动拉取，无需手动）
两个模型都依赖 `nvidia/Cosmos-Tokenizer-*`，HF 第一次推理时会自动下载到 cache，安装阶段不需手动处理。

### 6.4 备份占位（R14 fallback）

若 Predict2.5 + Drive-Dreams **同时**下载彻底失败（HF 全线挂、镜像也挂），仅做占位：
```bash
git submodule add https://github.com/OpenDriveLab/Vista.git third_party/vista
```
**不要**在 install_plan 阶段切换到 Vista 当主，仅占位等用户决策。Drive-Dreams 单独失败时优先重试，不要立即 fallback。

---

## 7. 数据集 [部分 BLOCKING]

> 数据策略 D3：MVP 用免审批数据。审批类数据并行启动但不阻塞。

### 7.1 nuScenes mini（~3 GB）[BLOCKING，免审批 MVP]
- 注册 nuscenes.org（用户操作）→ 下载 v1.0-mini → 解压到 `data/nuscenes/mini/`
- 验证：`data/nuscenes/mini/{maps,samples,sweeps,v1.0-mini}/` 四个子目录齐全。

### 7.2 DAIR-V2X-V example 子集 [BLOCKING]
- Google Drive 链接见 DAIR-V2X 仓库 README → 下载 example 子集（~5 GB）→ `data/dair_v2x_v_example/`
- 这是免审批的小样本，全集需邮件申请（见 7.6）。

### 7.3 ApolloScape 北京段 [BLOCKING]
- apolloscape.auto → Scene Parsing / 3D Lidar 北京段（~50 GB）→ `data/apolloscape/beijing/`
- 项目自研非商用，许可证 OK。

### 7.4 DrivingDojo HF [BLOCKING]
```bash
huggingface-cli login                          # 接受条款
HF_ENDPOINT=https://hf-mirror.com \
huggingface-cli download Yuqi1997/DrivingDojo \
  --repo-type dataset \
  --local-dir data/drivingdojo
```
- 约 100 GB，是 Cosmos LoRA 训练的素材源。

### 7.5 ONCE 全集 [OPTIONAL，并行申请]
- 表单：once-for-auto-driving.github.io → 提交 → 等审批（30–60 天）。
- agent **不要**尝试自动提交，**生成给用户的申请清单**写到 `docs/data_requests.md`：申请人姓名邮箱、用途说明草稿、收件邮箱。

### 7.6 DAIR-V2X 全集 [OPTIONAL，并行申请]
- 邮件 dair@air.tsinghua.edu.cn，同上：生成申请草稿到 `docs/data_requests.md`，不发邮件。

---

## 8. 评测：NAVSIM v2 [BLOCKING]

```bash
cd third_party
git submodule add https://github.com/autonomousvision/navsim.git
cd navsim && pip install -e . && cd ../..
```
- **重点**：NAVSIM v2 metric 库可以 `import`，但 EPDMS **不能裸调**——需要 Scene pickle adapter（D7、R12，~1 周开发量），那是 Day 5 的开发任务，不属于安装范围。
- 预下载 navhard_two_stage 评测包（如 README 提供）到 `data/navsim_packs/`。

### HUGSIM [OPTIONAL，Phase 3]
仅 `git submodule add https://github.com/hyzhou404/HUGSIM.git third_party/hugsim`，不装依赖。

---

## 9. 安装顺序与并行度建议

串行依赖：
1. 节 1（Python env）→ 必须最早
2. 节 5.1（gsplat 编译）→ 依赖节 1 的 PyTorch
3. 节 6.3.1 / 6.3.2（Cosmos 两个推理栈）→ 依赖节 1；**先装 Predict2.5，再装 Drive-Dreams**（如冲突则建副 env，主 env 别破坏）

可并行：
- 节 2（docker pull） / 节 3 / 节 4 / 节 7 之间无依赖，可后台并行下载。
- 大文件下载（Predict2.5 32G、Drive-Dreams 28G、ApolloScape 50G、DrivingDojo 100G）放后台 `nohup`，不要阻塞 agent 主线。
- Predict2.5 与 Drive-Dreams 权重可以**同时**下（HF 两个 repo 互不影响），但若带宽紧张先 Predict2.5（B-cn 是主报告 backend）。

---

## 10. 验收清单（agent 完成后填表）

| 项 | 状态 | 路径 / 版本 | 大小 | 备注 |
|---|---|---|---|---|
| Python 3.10 + torch 2.4 + CUDA 12.1 | ☐ | conda env `autosim` | — | `torch.cuda.is_available()` True |
| docker carla:0.9.16 | ☐ | image id | ~10 GB | 未启动 |
| docker carla:0.10.0 | ☐ | image id | ~12 GB | 未启动 |
| scenario_runner submodule | ☐ | commit hash | — | requirements 已装 |
| Bench2Drive submodule | ☐ | commit hash | — | requirements 未装（推迟） |
| SparseDriveV2 + ResNet-34 | ☐ | `third_party/SparseDriveV2` | ~100 MB | requirements 已装 |
| Senna + 权重 | ☐ | `third_party/Senna` + HF cache | ~14 GB | vicuna 已下 |
| gsplat ≥1.5.0 | ☐ | pip show gsplat | — | CUDA 编译通过 |
| DriveStudio | ☐ | `third_party/drivestudio` | — | requirements 已装 |
| Cosmos-Predict2.5-2B 权重（B-cn 基座）| ☐ | `models/cosmos-predict2.5-2b` | ~32 GB | OML 已接受 |
| cosmos-predict2.5 推理库 | ☐ | `third_party/cosmos-predict2.5` | — | `pip install -e .` 通过 |
| Cosmos-Drive-Dreams-7B 权重（B-av 直出）| ☐ | `models/cosmos-drive-dreams-7b` | ~28 GB | OML 已接受 |
| cosmos-transfer1 推理库 | ☐ | `third_party/cosmos-transfer1` | — | Drive-Dreams 走 transfer1 栈 |
| Cosmos-Drive-Dreams 工具仓 | ☐ | `third_party/Cosmos-Drive-Dreams` | — | HD map + bbox conditioning 转换 |
| 依赖隔离决策 | ☐ | 单 env 或双 env | — | 冲突则建 `autosim-drive-dreams` 副 env |
| nuScenes mini | ☐ | `data/nuscenes/mini` | ~3 GB | 4 子目录齐 |
| DAIR-V2X-V example | ☐ | `data/dair_v2x_v_example` | ~5 GB | — |
| ApolloScape 北京 | ☐ | `data/apolloscape/beijing` | ~50 GB | — |
| DrivingDojo HF | ☐ | `data/drivingdojo` | ~100 GB | — |
| NAVSIM v2 | ☐ | `third_party/navsim` | — | `import navsim` OK |
| 申请类（ONCE / DAIR-V2X 全集） | ☐ | `docs/data_requests.md` | — | 草稿生成，待用户发邮件 |

---

## 11. 完成后产出

- `docs/install_report.md`：每节命令、产物、磁盘、md5、耗时
- `docs/data_requests.md`：ONCE / DAIR-V2X 申请草稿
- `requirements.txt`：本次安装期间 pip 装过的所有包（pinned 版本）
- `environment.yml`：conda env 导出
- 不修改 `src/autosim/`、不创建新包骨架（不在范围内）

完成上述清单后，**停下来**汇报给用户，等待 W1 Day 1 的 hello-world 启动指令。
