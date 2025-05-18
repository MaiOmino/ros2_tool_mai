import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor

from lifecycle_msgs.srv import GetState, ChangeState
from lifecycle_msgs.msg import Transition

from argparse import ArgumentParser
import time

class LifecycleNodeActivator(Node):
    def __init__(self, node_name: str):
        super().__init__('lifecycle_node_activator')

        self.node_name = node_name
    
        self.get_state_srv = f'/{self.node_name}/get_state'
        self.change_state_srv = f'{self.node_name}/change_state'

        self.get_logger().info(f'Initializing for node: {self.node_name}')

        self.get_state_cli = self.create_client(GetState, self.get_state_srv)
        self.change_state_cli = self.create_client(ChangeState, self.change_state_srv)

        self.wait_for_services()
        self.handle_lifecycle()

    def wait_for_services(self):
        while not self.get_state_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'Waiting for {self.get_state_srv}...')
        
        while not self.change_state_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'Waiting for {self.change_state_srv}...')
    
    def change_state(self, transition_id, label, retries=-1, delay_sec=5.0):
        attempt = 0
        while retries == -1 or attempt < retries:
            attempt =+ 1
            req = ChangeState.Request()
            req.transition.id = transition_id
            future = self.change_state_cli.call_async(req)
            rclpy.spin_until_future_complete(self, future)

            if future.result().success:
                self.get_logger().info(f'{label} transition succeeded.')
                return True
            else:
                self.get_logger().warn(f'{label} transition failed on atempt {attempt}. Retrying in {delay_sec} sec...')
                time.sleep(delay_sec)
        
        self.get_logger().error(f'{label} transition failed after {retries} attempts.')
        return False
    
    def handle_lifecycle(self):
        get_state_req = GetState.Request()
        future = self.get_state_cli.call_async(get_state_req)
        rclpy.spin_until_future_complete(self, future)
        state = future.result().current_state
        state_id = state.id

        self.get_logger().info(f'{self.node_name} current state: {state.label} (id={state.id})')

        if state_id == 1: # unconfigured
            self.get_logger().info(f'{self.node_name} is unconfigured. Attempting to configure...')
            if not self.change_state(Transition.TRANSITION_CONFIGURE, "Configure"):
                return
            
            self.handle_lifecycle()
        
        elif state_id == 2: # inactive
            self.get_logger().info(f'{self.node_name} is inactive. Attempting to activate...')
            self.change_state(Transition.TRANSITION_ACTIVATE, "Activate")
        
        elif state_id == 3: # active
            self.get_logger().info(f'{self.node_name} is already active.')
        
        else:
            self.get_logger().info(f'{self.node_name} is in unsupported state: {state.label} (id={state.id})')


def main(args=None):
    parser = ArgumentParser(description='Activate a ROS2 Lifecycle Node if not already active')
    parser.add_argument('--node-name', type=str, required=True, help='Name of the lifecycle node (e.g., map_server)')
    parsed_args = parser.parse_args()

    rclpy.init(args=args)
    executor = SingleThreadedExecutor()
    
    try:
        node = LifecycleNodeActivator(parsed_args.node_name)
        executor.add_node(node)
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()