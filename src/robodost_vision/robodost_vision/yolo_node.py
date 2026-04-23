"""
YOLO Node (Object Detection)
"""
import rclpy
from rclpy.node import Node

class YoloNode(Node):
    def __init__(self):
        super().__init__('yolo_node')
        self.get_logger().info('YOLO Node started')
        # TODO: Initialize YOLOv8-nano via TensorRT
        # TODO: Subscribe to USB camera frame topic
        # TODO: Publish bounding boxes to Context Store

def main(args=None):
    rclpy.init(args=args)
    node = YoloNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
