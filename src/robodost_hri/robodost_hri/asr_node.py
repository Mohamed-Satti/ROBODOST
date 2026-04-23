"""
ASR Node (Automatic Speech Recognition)
"""
import rclpy
from rclpy.node import Node

class ASRNode(Node):
    def __init__(self):
        super().__init__('asr_node')
        self.get_logger().info('ASR Node started')
        # TODO: Initialize faster-whisper-tiny model
        # TODO: Subscribe to VAD audio chunks
        # TODO: Publish decoded text to text topics

def main(args=None):
    rclpy.init(args=args)
    node = ASRNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
