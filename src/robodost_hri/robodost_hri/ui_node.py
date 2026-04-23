"""
UI Node (User Interface)
"""
import rclpy
from rclpy.node import Node

class UINode(Node):
    def __init__(self):
        super().__init__('ui_node')
        self.get_logger().info('UI Node started')
        # TODO: Initialize facial expression tracking / visual interactions
        # TODO: Subscribe to /emergency/status for visual warning

def main(args=None):
    rclpy.init(args=args)
    node = UINode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
