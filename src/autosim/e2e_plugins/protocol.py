"""E2E 自动驾驶算法插件统一协议。

仿真器与算法之间唯一的契约。新算法只需实现 ``E2EPlanner`` 协议，
无需修改仿真器内部。仿真器只消费 ``Action.trajectory``，由
``autosim.kinematics`` 的 Pure Pursuit/LQR 跟踪器驱动车辆，
确保算法与车辆动力学完全解耦。
"""

from __future__ import annotations

from typing import Optional, Protocol, TypedDict, runtime_checkable

import numpy as np


class Observation(TypedDict, total=False):
    images: dict[str, np.ndarray]
    """{cam_id: HxWx3 uint8 RGB}; cam_id 用 nuScenes 命名规范 (CAM_FRONT, CAM_FRONT_LEFT, ...)。必填。"""

    intrinsics: dict[str, np.ndarray]
    """{cam_id: 3x3 float}。必填。"""

    extrinsics: dict[str, np.ndarray]
    """{cam_id: 4x4 float, cam->ego}。必填。"""

    ego_state: dict
    """{'v': float (m/s), 'a': float (m/s^2), 'yaw_rate': float (rad/s), 'steer': float (rad)}。必填。"""

    timestamp: float
    """秒，单调递增。必填。"""

    nav_command: Optional[str]
    """高层导航指令: 'LEFT' | 'RIGHT' | 'STRAIGHT' | 'FOLLOW' | 'CHANGE_LANE_LEFT' | 'CHANGE_LANE_RIGHT'。"""

    route: Optional[np.ndarray]
    """ego 系下未来路由点, Nx2 (x, y) m。VAD/UniAD 等需要全局路由的算法用。"""

    hd_map: Optional[dict]
    """矢量地图 (lane/crosswalk/stop_line)。仅依赖 GT HD map 的算法需要。生产线上一般 None。"""


class Action(TypedDict, total=False):
    trajectory: np.ndarray
    """K x 3 (x, y, heading)，ego 系，t=0 处于自车。仿真器消费这一项。必填。

    默认 K=6, dt=0.5s (与 NAVSIM/Bench2Drive 习惯一致)。算法可输出更密的轨迹，
    仿真器在跟踪器层做内插。
    """

    trajectory_modes: Optional[np.ndarray]
    """M x K x 3 多模态轨迹候选。仿真器默认取 argmax(mode_probs)；评测可全用。"""

    mode_probs: Optional[np.ndarray]
    """M, 多模态概率分布。"""

    control: Optional[dict]
    """{'steer': rad, 'accel': m/s^2}。Tesla 风格直接控制；指定时仿真器跳过跟踪器。"""

    meta: dict
    """{'inference_time_ms': float, 'text_explanation': str?, 'log': dict?}。诊断用。"""


@runtime_checkable
class E2EPlanner(Protocol):
    """所有 E2E 算法插件必须满足此协议。

    生命周期::

        planner.reset(scenario_meta)
        for tick in range(T):
            obs = simulator.observe()
            action = planner.step(obs)
            simulator.advance(action)
        planner.close()
    """

    def reset(self, scenario_meta: dict) -> None:
        """场景开始时调用。

        Parameters
        ----------
        scenario_meta:
            ``{'ego_init_pose': (x, y, heading), 'route': Nx2, 'weather': str,
            'scenario_id': str, 'dt': float, 'horizon_s': float}``。
        """
        ...

    def step(self, obs: Observation) -> Action:
        """每个仿真 tick 调用一次（默认 10 Hz）。"""
        ...

    def close(self) -> None:
        """场景结束时调用。释放显存等。"""
        ...


__all__ = ["Observation", "Action", "E2EPlanner"]
