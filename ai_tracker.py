#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class AITrackerNode(Node):
    def __init__(self):
        super().__init__('ai_tracker_node')
        self.bridge = CvBridge()
        self.sub_image = self.create_subscription(Image, '/camera', self.image_callback, 10)
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 動作開始フラグ（最初は停止状態で待機）
        self.is_running = False
        self.get_logger().info('Ready! カメラ画面を選択して [SPACE] キーを押すと追従を開始します。')

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        height, width, _ = cv_image.shape
        center_x = width // 2

        # 赤色ボールを検出（HSV色空間）
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255]))
        mask = mask1 | mask2

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        twist = Twist()

        target_detected = False
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 100:
                target_detected = True
                (x, y), radius = cv2.minEnclosingCircle(largest_contour)
                error_x = (x - center_x) / (width / 2.0)
                
                # 追従指令の計算
                twist.angular.z = -1.5 * error_x
                if radius < 45:
                    twist.linear.x = 0.3
                elif radius > 55:
                    twist.linear.x = -0.1
                else:
                    twist.linear.x = 0.0

                # 検出マーカー（緑の円）を描画
                cv2.circle(cv_image, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                cv2.putText(cv_image, f"Target: r={int(radius)}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 画面上に現在のステータスを表示
        if not self.is_running:
            cv2.putText(cv_image, "STATUS: WAITING (Press SPACE)", (10, height - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        else:
            cv2.putText(cv_image, "STATUS: ACTIVE", (10, height - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # 追従実行中のみ司令を発行（見失っている場合は周囲を探索）
            if not target_detected:
                twist.angular.z = 0.4
            self.pub_cmd.publish(twist)

        cv2.imshow("Robot Camera View (AI Detection)", cv_image)
        
        # キー入力判定
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACEキーで開始/一時停止を切り替え
            self.is_running = not self.is_running
            state = "開始" if self.is_running else "一時停止"
            self.get_logger().info(f'追従を {state} しました。')
            if not self.is_running:
                self.pub_cmd.publish(Twist())  # 停止
        elif key == 27:  # ESCキーで終了
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = AITrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.pub_cmd.publish(Twist())
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
