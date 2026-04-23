"""
Hardware Bridge Node (Arduino Comms)
"""
import rclpy
from rclpy.node import Node

class HardwareBridgeNode(Node):
    def __init__(self):
        super().__init__('hardware_bridge_node')
        self.get_logger().info('Hardware Bridge Node started')
        # TODO: Initialize Serial UART bridge with Arduino
        # TODO: Subscribe to PID and motion commands from orchestrator
        # TODO: Transmit hard real-time execution payloads

def main(args=None):
    rclpy.init(args=args)
    node = HardwareBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
