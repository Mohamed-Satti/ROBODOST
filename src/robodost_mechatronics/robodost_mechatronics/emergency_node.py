"""
Emergency Node (Software Kill-switch)
"""
import rclpy
from rclpy.node import Node

class EmergencyNode(Node):
    def __init__(self):
        super().__init__('emergency_node')
        self.get_logger().info('Emergency Node started')
        # TODO: Monitor Jetson GPIO pin for external analog red button press
        # TODO: Instantly flag /emergency/status = true if triggered
        # TODO: Manage software side of dual-path emergency priority

def main(args=None):
    rclpy.init(args=args)
    node = EmergencyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
