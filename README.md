# Gazebo × ROS 2 による車載ビジョンを用いた物体認識・自律追従ロボット

## 1. 概要
Gazebo (Ignition Fortress) 上の差動二輪ロボットに車載カメラを搭載し、ROS 2 Humble と連携して特定ターゲット（赤いボール）を自律認識・追従するシステムです。
OpenCVを用いた色空間抽出によりターゲットの画像座標・距離を算出し、P制御によってロボットの走行速度（/cmd_vel）を自動制御します。

## 2. 構成ファイル
- `world.sdf`: 車載カメラセンサ、差動駆動プラグイン、および追従ターゲット（球体）を定義したGazeboワールドファイル。
- `ai_tracker.py`: カメラ画像を購読し、ターゲット認識および自律追従速度指令をパブリッシュするROS 2ノード。

## 3. 動作環境
- OS: Ubuntu 22.04 LTS (Docker環境)
- ROS 2: Humble
- シミュレータ: Gazebo (Ignition Fortress)
- 主要パッケージ: `ros_ign_bridge`, `cv_bridge`, `opencv-python`

## 4. 実行手順
1. **Gazeboの起動**
   ```bash
   cd ~/gazebo_test
   ign gazebo world.sdf
