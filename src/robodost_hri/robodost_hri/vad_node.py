"""
VAD Node (Voice Activity Detection)
"""
import rclpy
from rclpy.node import Node

class VADNode(Node):
    def __init__(self):
        super().__init__('vad_node')
        self.get_logger().info('VAD Node started')
        # TODO: Initialize Silero VAD
        # TODO: Route active voice segments to ASR Node

def main(args=None):
    rclpy.init(args=args)
    node = VADNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
