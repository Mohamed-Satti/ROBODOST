"""
Orchestrator Node (FSM Action Engine)
"""
import rclpy
from rclpy.node import Node

class OrchestratorNode(Node):
    def __init__(self):
        super().__init__('orchestrator_node')
        self.get_logger().info('Orchestrator Node started')
        # TODO: Implement State Machine (IDLE -> LISTENING -> PROCESSING -> EXECUTING -> IDLE)
        # TODO: Handle barge-in/preemption (visual wake word/audio keyword)
        # TODO: Intercept /emergency/status globally to cancel all queues

def main(args=None):
    rclpy.init(args=args)
    node = OrchestratorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
