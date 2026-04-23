"""
Wake Word Node
"""
import rclpy
from rclpy.node import Node

class WakeWordNode(Node):
    def __init__(self):
        super().__init__('wakeword_node')
        self.get_logger().info('Wake Word Node started')
        # TODO: Implement auditory keyword spotting
        # TODO: Subscribe to continuous audio stream
        # TODO: Publish barge-in events to orchestrator

def main(args=None):
    rclpy.init(args=args)
    node = WakeWordNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
