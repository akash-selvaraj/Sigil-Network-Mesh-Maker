import numpy as np
import random
from collections import deque
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

class DQNAgent:
    def __init__(self, state_size, action_size, alpha=0.001, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_min = epsilon_min  # Minimum exploration rate
        self.epsilon_decay = epsilon_decay  # Exploration decay rate
        self.learning_rate = alpha  # Learning rate
        self.model = self._build_model()  # Build the DQN model

    def _build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))  # Output layer
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)  # Explore
        q_values = self.model.predict(state)  # Predict Q-values for the given state
        return np.argmax(q_values[0])  # Exploit

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])  # Bellman equation
            target_f = self.model.predict(state)
            target_f[0][action] = target  # Update the target Q-value
            self.model.fit(state, target_f, epochs=1, verbose=0)  # Fit the model

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay  # Decay epsilon

    def save(self, dqn_saved):
        self.model.save(dqn_saved)

    def load(self, dqn_saved):
        self.model.load_weights(dqn_saved)

# Example usage
if __name__ == '__main__':
    state_size = 4  # Define state size based on your application
    action_size = 4  # Example: left, right, up, down
    agent = DQNAgent(state_size, action_size)

    # Example of using the agent
    state = np.reshape([1, 0, 0, 0], [1, state_size])  # Example initial state
    action = agent.choose_action(state)
    print(f"Chosen Action: {action}")
