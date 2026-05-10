# Milestone 1 Report

## 阶段 0.2 CARLA docker 实测记录

- 测试时间：2026-05-10
- 测试主机：Ubuntu 22.04，NVIDIA GeForce RTX 3080 Ti（driver 570.153.02）
- 目标要求：`carlasim/carla:0.9.16` 可拉取，`--RenderOffScreen` 启动 Town10，30 秒不 crash，并记录 fps + 显存占用

### 0.2.1 环境准备

- 安装 `docker.io`（29.1.3）
- 安装并配置 `nvidia-container-toolkit`（1.19.0）
- Docker 运行时确认包含 `nvidia`
- GPU 容器可见性确认：容器内 `nvidia-smi` 正常识别 3080 Ti

### 0.2.2 CARLA 镜像拉取

- 镜像：`carlasim/carla:0.9.16`
- 结果：拉取成功
- digest：`sha256:aaf1df22702780ece072069e23d03c4879b002ae028c79744b09c4c7ddbae953`

### 0.2.3 30 秒稳定性验证（Town10，OffScreen）

- 启动命令（示例）：

```bash
docker run -d --rm --runtime=nvidia --gpus all --name carla_m1 --net=host --ipc=host \
  -e NVIDIA_DRIVER_CAPABILITIES=all -e SDL_AUDIODRIVER=dummy \
  carlasim/carla:0.9.16 \
  /bin/bash -lc "cd /workspace && ./CarlaUE4.sh -RenderOffScreen -quality-level=Low -carla-map=Town10HD -carla-world-port=2000"
```

- 35 秒存活检查：`Up 35 seconds`
- 额外运行时检查：`Up 59 seconds`
- 结论：满足“30 秒不 crash”验收要求

### 0.2.4 fps 与资源占用

- fps（host 端 CARLA PythonAPI 对 `localhost:2000` 连续 `wait_for_tick` 15 秒）：
  - `ticks=1418`
  - `elapsed=15.010`
  - `fps=94.473`
  - 原始记录保存在本机 `others/carla_*`，不纳入 git

- GPU 显存与利用率（30 个采样点，1 Hz）：
  - `gpu_util_avg=28.43%`
  - `gpu_util_max=55%`
  - `mem_used_avg=4534.13 MiB`
  - `mem_used_max=5037 MiB`
  - `mem_total=12288 MiB`

- Docker 单点资源：
  - `cpu=236.80%`
  - `mem=3.145GiB / 31.34GiB`

### 0.2.5 备注

- 若直接以默认路径/参数启动，可能触发软件 Vulkan（`lavapipe`）导致渲染线程超时崩溃；本次采用 `nvidia-container-toolkit` + `--gpus all` 的 GPU 路径并通过稳定性验证。
- 当前机器为 3080 Ti；里程碑部署目标 A800（同属 Ampere）应具备同等或更优的运行余量。

## 阶段 0.3 数据下载与加载校验

### 0.3.1 nuScenes mini 下载

- 下载地址：`https://www.nuscenes.org/data/v1.0-mini.tgz`
- 本地路径：`data/nuscenes/mini/v1.0-mini.tgz`
- 归档大小：约 `3.9G`
- 解压目录：`data/nuscenes/mini/`

### 0.3.2 目录结构验收

- 已验证以下目录存在：
  - `data/nuscenes/mini/maps/`
  - `data/nuscenes/mini/samples/`
  - `data/nuscenes/mini/sweeps/`
  - `data/nuscenes/mini/v1.0-mini/`

### 0.3.3 nuscenes-devkit 加载验证

- 安装：`python3 -m pip install --user nuscenes-devkit`
- 验证脚本（核心）：

```python
from nuscenes.nuscenes import NuScenes
nusc = NuScenes(version="v1.0-mini", dataroot="data/nuscenes/mini", verbose=False)
print(len(nusc.scene), len(nusc.sample), len(nusc.sample_data))
```

- 实测结果：
  - `scene_count=10`
  - `sample_count=404`
  - `sample_data_count=31206`

- 结论：`sample`/`sample_data` 表加载正常，任务 0.3 验收通过。

## 阶段 0.4 模型权重准备

### 0.4.1 官方权重来源

- SparseDriveV2 官方仓库：`https://github.com/swc-17/SparseDriveV2`
- README 权重链接（NAVSIMv2 90.3）：`https://huggingface.co/wenchaosun/SparseDriveV2/resolve/main/sparsedrive_navsimv2_90p3.ckpt`
- ResNet-34 backbone（timm a1_in1k）：`https://huggingface.co/timm/resnet34.a1_in1k/resolve/main/pytorch_model.bin`

### 0.4.2 下载与落盘

- 存放目录：`checkpoints/sparsedrive_v2/`
- 文件列表：
  - `checkpoints/sparsedrive_v2/sparsedrive_navsimv2_90p3.ckpt`（约 518M）
  - `checkpoints/sparsedrive_v2/resnet34.a1_in1k.pytorch_model.bin`（约 84M）

### 0.4.3 完整性校验（SHA256）

- `sparsedrive_navsimv2_90p3.ckpt`
  - `b22438dbf8a5966ea532599ba6cf905e599594e758938b8fbab1f6bd257cbc4b`
- `resnet34.a1_in1k.pytorch_model.bin`
  - `f6c1d7785b5d0e796a83f9643fe2cb952ac95740daa9fb2d5c8c6514fdadaeb3`

### 0.4.4 配置文件

- 已新增：`configs/sparsedrive_v2.yaml`
- 已写入：
  - checkpoint 路径
  - backbone 路径
  - 下载源 URL
  - SHA256 校验值

- 结论：任务 0.4 验收通过。

## 阶段 0.5 Submodules

### 0.5.1 已添加子模块

- `third_party/scenario_runner` ← `https://github.com/carla-simulator/scenario_runner.git`
- `third_party/bench2drive` ← `https://github.com/Thinklab-SJTU/Bench2Drive.git`
- `third_party/sparsedrive_v2` ← `https://github.com/swc-17/SparseDriveV2.git`

### 0.5.2 提交点校验

- `third_party/scenario_runner`: `94ff3b8`
- `third_party/bench2drive`: `8d587ec`
- `third_party/sparsedrive_v2`: `c4c2ac1`

### 0.5.3 备注

- 仓库内已有一个历史异常 gitlink（`.claude/worktrees/...`）导致 `git submodule status --recursive` 全量命令报错，但不影响本次新增三个 submodule 的 clone 与 gitlink 记录（`.gitmodules` + `third_party/*` 均已入索引）。
- 结论：任务 0.5 验收通过。

## 阶段 0.6 包骨架

### 0.6.1 目录结构

- 已补齐 `src/autosim/` 子包结构：
  - `core/`
  - `renderer/`
  - `renderer/carla_ue4/`
  - `kinematics/`
  - `scenarios/`
  - `e2e_plugins/`（原有）
  - `data_adapters/`
  - `eval/`

### 0.6.2 占位文件

- 已新增以下 `__init__.py`：
  - `src/autosim/core/__init__.py`
  - `src/autosim/renderer/__init__.py`
  - `src/autosim/renderer/carla_ue4/__init__.py`
  - `src/autosim/kinematics/__init__.py`
  - `src/autosim/scenarios/__init__.py`
  - `src/autosim/data_adapters/__init__.py`
  - `src/autosim/eval/__init__.py`

### 0.6.3 协议文件确认

- `src/autosim/e2e_plugins/protocol.py` 已存在且未改动。

- 结论：任务 0.6 验收通过。
