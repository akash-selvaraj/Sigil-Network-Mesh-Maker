import random
from pymongo import MongoClient

def calculate_direction(current_position, next_position):
    """Calculate movement directions based on position changes."""
    delta_x = next_position[0] - current_position[0]
    delta_y = next_position[1] - current_position[1]
    direction = []

    if delta_y > 0:
        direction.append(f"Move north by {abs(delta_y)} meter(s)")
    elif delta_y < 0:
        direction.append(f"Move south by {abs(delta_y)} meter(s)")

    if delta_x > 0:
        direction.append(f"Move east by {abs(delta_x)} meter(s)")
    elif delta_x < 0:
        direction.append(f"Move west by {abs(delta_x)} meter(s)")

    return direction

class SignalRLAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = {}  # Q-Table for storing state-action values
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.actions = actions  # Possible actions [left, right, up, down]

    def get_q_value(self, state, action):
        return self.q_table.get((tuple(state), action), 0.0)

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)  # Explore: random action
        q_values = [self.get_q_value(state, action) for action in self.actions]
        max_q = max(q_values)
        return self.actions[q_values.index(max_q)]  # Exploit: choose best action

    def update_q_value(self, state, action, reward, next_state):
        max_q_next = max([self.get_q_value(next_state, a) for a in self.actions])
        old_q = self.get_q_value(state, action)
        new_q = old_q + self.alpha * (reward + self.gamma * max_q_next - old_q)
        self.q_table[(tuple(state), action)] = new_q

    def update_agent_with_speed_data(self, current_position, current_upload_speed, current_download_speed, mesh_collection):
        action = self.choose_action(current_position)

        # Update position based on chosen action
        next_position = current_position[:]
        if action == 'left':
            next_position[0] -= 1
        elif action == 'right':
            next_position[0] += 1
        elif action == 'up':
            next_position[1] += 1
        elif action == 'down':
            next_position[1] -= 1

        # Fetch signal data from the database for the next position
        next_position_data = mesh_collection.find_one({'position': next_position})

        if next_position_data:
            predicted_download_speed = next_position_data.get('download_speed', 0.0)
            predicted_upload_speed = next_position_data.get('upload_speed', 0.0)
        else:
            predicted_download_speed = 0.0
            predicted_upload_speed = 0.0

        # Calculate reward
        reward = self.get_reward(current_download_speed, current_upload_speed, predicted_download_speed, predicted_upload_speed)

        # Update Q-value
        self.update_q_value(current_position, action, reward, next_position)

        # Get directions
        direction = calculate_direction(current_position, next_position)

        return {
            'recommended_action': action,
            'next_position': next_position,
            'direction': direction,
            'predicted_download_speed': predicted_download_speed,
            'predicted_upload_speed': predicted_upload_speed,
        }

    def get_reward(self, current_download_speed, current_upload_speed, predicted_download_speed, predicted_upload_speed):
        download_speed_change = predicted_download_speed - current_download_speed
        upload_speed_change = predicted_upload_speed - current_upload_speed

        reward = (0.7 * download_speed_change) + (0.3 * upload_speed_change)
        return reward

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
db = client['signal_map_db']  # Replace with your database name
mesh_collection = db['mesh_points']  # Replace with your collection name

# Example usage
if __name__ == '__main__':
    actions = ['left', 'right', 'up', 'down']
    q_agent = SignalRLAgent(actions)

    # Simulate getting data and updating the agent
    current_position = [0, 0]  # Example starting position
    current_upload_speed = 10.0  # Example initial upload speed
    current_download_speed = 20.0  # Example initial download speed

    result = q_agent.update_agent_with_speed_data(
        current_position, current_upload_speed, current_download_speed, mesh_collection
    )

    print(f"Next Position: {result['next_position']}, Action: {result['recommended_action']}, "
          f"Predicted Download Speed: {result['predicted_download_speed']}, "
          f"Predicted Upload Speed: {result['predicted_upload_speed']}, Directions: {result['direction']}")
