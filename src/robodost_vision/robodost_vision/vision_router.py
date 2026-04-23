"""
Vision Router Node
"""
import rclpy
from rclpy.node import Node

class VisionRouter(Node):
    def __init__(self):
        super().__init__('vision_router')
        self.get_logger().info('Vision Router started')
        # TODO: Route camera frames efficiently between YOLO and MediaPipe 
        # TODO: Handle disabling frames locally when watchdog triggers Mode 2

def main(args=None):
    rclpy.init(args=args)
    node = VisionRouter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
