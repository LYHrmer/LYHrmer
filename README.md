## LYH

- 研究方向:多智能体路径规划(MAPF),终身场景下的执行层调度
- 控制:LQR、滑模、ESO、阻抗与力位混合、约束 MPC、VMC,配套递推最小二乘辨识
- 实现:STM32 裸机 C,以及 MuJoCo / Isaac Lab 里的可复现验证

### 控制算法

**[robot-arm-compliant-control-lab](https://github.com/LYHrmer/robot-arm-compliant-control-lab)** — Franka 7-DOF 阻抗、导纳与力位混合控制,500 Hz 接触状态机。在线切向补偿把跟踪误差从 1.885 压到 1.359 mm;Python 与 C++ 两套实现对齐 16.8 万周期。

**[wheel-legged-control-lab](https://github.com/LYHrmer/wheel-legged-control-lab)** — D1 轮足整机(23 nq / 16 执行器),VMC、LQR、约束 MPC 与残差 PPO 共用同一控制循环,轮心 Jacobian 做支撑力分配。

**[gimbal-lqr-eso](https://github.com/LYHrmer/gimbal-lqr-eso)** — 动力学前馈 + 离散 LQR + ESO 扰动观测的云台控制器,含抗饱和积分与在线参数辨识。C11,不依赖 HAL 和 RTOS。

**[gimbal-smc-controller](https://github.com/LYHrmer/gimbal-smc-controller)** — 线性滑模加可选正则化终端项,纯 C99。576 组模型组合闭环仿真验证。

**[Rudder-Swerve-Control](https://github.com/LYHrmer/Rudder-Swerve-Control)** — 四舵轮运动学解算、就近最优角与 cos³ 轮速补偿,2 ms 控制周期。2023–2026 赛季实车代码。

### 规划与决策

**[atec-robotics-projects](https://github.com/LYHrmer/atec-robotics-projects)** — ATEC 2026 仿真。四足带臂 RGB-D 闭环导航连续越障 286 m,残差 PPO 适配带臂机体与复杂地形;手写点云聚类抓取几何链配 DLS 解析 IK,抓取 18/18。

**[robot-vision-control-lab](https://github.com/LYHrmer/robot-vision-control-lab)** — 从一帧图像到有界速度命令:四路 PnP 方案对比 + body-frame SE(3) 比例控制。PnP 6.03 mm / 1.06°,位姿伺服 4.44 s 收敛。

### 技术栈

最优控制与鲁棒控制、力控与柔顺控制、系统辨识、多智能体路径规划、强化学习 · C99/C11、Python、C++ · MuJoCo、Isaac Lab、PyTorch、ONNX · STM32F4、FreeRTOS、CMSIS-DSP、CAN · OpenCV、相机标定、PnP · ROS/ROS2、CMake、pytest

---

