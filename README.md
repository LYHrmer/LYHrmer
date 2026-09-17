## LYH · 嵌入式与机器人控制

从 STM32 上跑 2 ms 周期的裸机 C，到 MuJoCo / Isaac Sim 里可复现的闭环验证。

- 🎓 研究生在读，方向是**多智能体路径规划（MAPF）**与**机器人运动控制**
- 🤖 RoboMaster 电控：山东理工大学齐奇战队，**2023 赛季队长兼电控组组长**，2026 赛季随队打进复活赛
- 🔧 底层写 C（C99 / C11，不依赖 HAL 与 RTOS），上层写 Python（MuJoCo / Isaac Lab / PyTorch）
- 📐 习惯把控制器**先辨识、再仿真、再上车**，每一步都留可复查的数据

---

### 实车落地

赛场跑过的代码，不是仿真。

| 项目 | 做了什么 | 关键技术点 |
| :--- | :--- | :--- |
| **[Rudder-Swerve-Control](https://github.com/LYHrmer/Rudder-Swerve-Control)** ⭐11 | RoboMaster 四舵轮底盘控制层，2023–2026 赛季实车 | 就近最优角（8192 counts/圈绝对编码器，误差折返到 ±4096，舵机转动永不超 90°）、**cos³ 轮速补偿**、单精度 `sqrtf/atan2f` 压进 2 ms 控制周期、跟随/小陀螺/失能状态机 + 超级电容功率接口<br>`STM32F407 · FreeRTOS · CMSIS-DSP · CAN` |

### 嵌入式控制器

C 写的控制器 + 完整辨识与仿真验证链路。**尚无实机数据，仓库里已明确标注。**

| 项目 | 做了什么 | 验证结果 |
| :--- | :--- | :--- |
| **[gimbal-lqr-eso](https://github.com/LYHrmer/gimbal-lqr-eso)** ⭐4 | 云台控制器：动力学前馈 + 离散 LQR + ESO 扰动观测 + 抗饱和积分 | DM4310 Pitch 误差 **−72.5%**、GM6020 Yaw 配置增益 **−33.7%**；GM6020 同参对照 **+4.0%（变差，已公开）**<br>C11 · 静态状态 · 无动态分配 · Cortex-M4F 编译检查 |
| **[gimbal-smc-controller](https://github.com/LYHrmer/gimbal-smc-controller)** | 云台滑模控制器，可选正则化终端项 | **576 组**开源模型组合闭环仿真、**12 万次** RLS 数值回归、ASan/UBSan **13/13**、6 个 hard-float 静态库<br>纯 C99 · 无 HAL / RTOS / C++ / 堆 |

两个控制器都做了 **GM6020 电流模式（`0x1FE/0x2FE`）与 DM4310 MIT 纯力矩**双适配，以及在线 RLS 参数辨识。

### 机器人仿真与学习

| 项目 | 做了什么 | 可量化结果 |
| :--- | :--- | :--- |
| **[atec-robotics-projects](https://github.com/LYHrmer/atec-robotics-projects)** | ATEC 2026：D1+G2 连续越障、Piper RGB-D 抓取、B2wPiper 移动操作 | 越障**连续通过 286 m**，调参后 505.7 s → 457.3 s（**−9.6%**）；抓取 **18/18 满分**，三个 seed 复现；移动操作 43.9 s 得分、0 非法接触<br>残差 PPO（冻结基础策略）+ critic 非对称特权观测 · 手写 RGB-D 抓取几何链 · DLS 解析 IK + BC 残差 |
| **[robot-arm-compliant-control-lab](https://github.com/LYHrmer/robot-arm-compliant-control-lab)** | Franka 7-DOF 沿曲面擦拭，同时跟踪 12 N 法向接触力 | 在线切向补偿使 RMSE **1.885 → 1.359 mm**，24/24 全部改善；**Python↔C++ 一致性 168,000 周期，最大分量误差 < 3.6e-15**<br>阻抗 / 导纳 / 力位混合 · 500 Hz 接触状态机 · torque-safe 残差 RL · HMAC 派生种子的**盲测评估协议** |
| **[wheel-legged-control-lab](https://github.com/LYHrmer/wheel-legged-control-lab)** | D1 轮足整机（23 nq / 22 nv / 16 执行器）全身控制 | 留出道路速度 RMSE **0.0402 → 0.0333 m/s**，达标 **6/6**；键盘实测 0.31 / 0.41 / 0.50 m/s 三档<br>VMC · LQR · 约束 MPC · 残差 PPO 共用同一控制循环 · 轮心 Jacobian 支撑力分配 · checkpoint SHA-256 校验 |
| **[robot-vision-control-lab](https://github.com/LYHrmer/robot-vision-control-lab)** ⭐3 | 从一帧图像到有界速度命令的完整链路 | PnP **99% 接受 / 6.03 mm / 1.06°**（σ=1 px、10% 外点）；位姿伺服 **4.44 s 收敛到 4.97 mm / 0.994°**；ONNX parity **4.96e-5**；64×64 推理 p50 **0.759 ms**<br>四路 PnP 对比 · body-frame SE(3) 比例控制 + 死区 + 指数映射 · **29 个测试 + CI** |

---

### 技术栈

**嵌入式** `C99/C11` `STM32F4` `FreeRTOS` `CMSIS-DSP` `CAN` `GM6020 / DM4310` `超级电容功率控制`

**控制** `LQR` `滑模 SMC` `ESO` `阻抗/导纳/力位混合` `约束 MPC` `VMC` `递推最小二乘辨识`

**仿真与学习** `MuJoCo` `Isaac Sim / Isaac Lab` `PyTorch` `PPO / 残差 RL` `ONNX` `Webots / Gazebo`

**视觉** `OpenCV` `相机标定` `PnP` `实例分割` `视觉伺服` `MindVision MVSDK`

**其他** `Python` `C++` `ROS / ROS2` `CMake` `pytest / ctest` `GitHub Actions`

---

### 关于这些仓库怎么读

每个仓库都把**已验证**和**未验证**分开写，失败项照原样留着，不藏：

- Franka 残差 RL 在 48 例盲测里只过 22–26 例（门槛 44/48），主结果判 **FAIL**，明确写「不部署」
- 云台 LQR 在 GM6020 上同参对照 **+4.0%（变差）**，`all_primary_acceptance_passed: false` 原样公开
- 轮足 LQR 结构从开发道路 5/6 掉到留出道路 2/6，退化如实保留
- 两个评测 seed 产出逐字节相同的 CSV，因此**不给置信区间**

这么写是因为：拿到代码的人应该知道哪里已经踩过坑、哪里还不能用。仿真结果不冒充实机结果。

<sub>📫 联系方式待补充</sub>

<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=LYHrmer&layout=compact&langs_count=8&hide=powershell,html,mdx&theme=default&card_width=340" alt="Top languages" />
