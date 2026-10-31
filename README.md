# Gazebo × ROS 2 による車載ビジョンを用いた物体認識・自律追従ロボット

## 1. 概要
本プロジェクトは、シミュレータ「Gazebo (Ignition Fortress)」上の差動二輪ロボットに車載カメラを搭載し、「ROS 2 Humble」を介して特定ターゲット（赤いボール）を自律的に認識・追従・接近する自律走行システムです。
OpenCVを用いた色空間抽出によりターゲットの画像座標および距離を算出し、P制御（比例制御）によって走行速度（`/cmd_vel`）をリアルタイムに自動制御します。

## 2. 構成ファイル
- `world.sdf`: 車載カメラセンサ、差動駆動プラグイン（DiffDrive）、地面、光源、および追従ターゲット（赤い球体）を定義したGazeboワールドファイル。
- `ai_tracker.py`: カメラ画像（`/camera`）を購読し、ターゲット認識・追従速度指令（`/cmd_vel`）を計算・発行するROS 2 Pythonノード。

## 3. 動作環境
- **OS**: Ubuntu 22.04 LTS (Docker環境: `airobotbook/ros2-desktop-ai-robot-book-humble:latest`)
- **ROS 2**: Humble
- **シミュレータ**: Gazebo (Ignition Fortress)
- **主要依存ライブラリ**:
  - `ros-humble-ros-ign-bridge`
  - `ros-humble-cv-bridge`
  - `python3-opencv`
  - `numpy < 2.0`

## 4. 実行手順
本システムを動作させるには、ターミナルを3つ起動し、以下の順序で実行します。

### ターミナル1: Gazeboの起動
```bash
cd ~/gazebo_test
ign gazebo world.sdf
```
※ Gazeboウィンドウが起動したら、画面左下の再生ボタン（▶）をクリックしてシミュレーションを開始状態にしてください。

### ターミナル2: ROS 2 - Gazebo トピックブリッジの起動
```bash
ros2 run ros_ign_bridge parameter_bridge \
  /cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist \
  /camera@sensor_msgs/msg/Image[ignition.msgs.Image
```
※ 走行速度指令（ROS 2 → Gazebo）およびカメラ画像（Gazebo → ROS 2）の双方向トピック中継を確立します。

### ターミナル3: AI自律追従ノードの起動
```bash
cd ~/gazebo_test
python3 ai_tracker.py
```
※ 起動後、ポップアップするカメラ認識画面（`Robot Camera View (AI Detection)`）をクリックして選択し、キーボードの **[SPACE] キー** を押すとロボットの追従動作が開始されます（再度SPACEキーを押すと一時停止します）。
