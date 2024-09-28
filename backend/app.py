from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for Matplotlib
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from q_learning_agent import SignalRLAgent  # Q-learning agent
from dqn_agent import DQNAgent  # DQN agent
import random
from waitress import serve

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['signal_map_db']
mesh_collection = db['mesh_points']

# Initialize RL agents
ACTIONS = ['left', 'right', 'up', 'down']
state_size = 2  # Position (x, y) is the state
action_size = len(ACTIONS)

q_agent = SignalRLAgent(ACTIONS)  # Q-learning agent
dqn_agent = DQNAgent(state_size, action_size)  # DQN agent

# Helper function to insert data into MongoDB
def insert_mesh_point(mesh_point):
    mesh_collection.insert_one(mesh_point)

# API endpoint to submit data from the mobile app
@app.route('/submit_data', methods=['POST'])
def submit_data():
    data = request.json
    position = data.get('position')
    upload_speed = data.get('upload_speed')
    download_speed = data.get('download_speed')
    timestamp = data.get('timestamp')

    # Validate the received data
    if not all([position, upload_speed, download_speed, timestamp]):
        return jsonify({"error": "Missing required fields"}), 400

    # Insert the mesh point into the database
    mesh_point = {
        "position": position,  # [x, y]
        "upload_speed": upload_speed,
        "download_speed": download_speed,
        "timestamp": timestamp
    }
    insert_mesh_point(mesh_point)

    return jsonify({"status": "success"}), 201

# API endpoint to get a movement recommendation using Q-learning
@app.route('/get_q_learning_recommendation', methods=['GET'])
def get_q_learning_recommendation():
    try:
        # Fetch mesh points from MongoDB
        mesh_points = list(mesh_collection.find({}))
        if not mesh_points:
            return jsonify({"error": "No data available"}), 404

        # Get current position and speed data
        current_point = mesh_points[-1]  # Last recorded point
        current_position = current_point.get('position')
        current_upload_speed = current_point.get('upload_speed')
        current_download_speed = current_point.get('download_speed')

        if current_position is None or current_upload_speed is None or current_download_speed is None:
            return jsonify({"error": "Invalid data in the database"}), 400

        # Update the RL agent based on current upload and download speeds
        result = q_agent.update_agent_with_speed_data(
            current_position, current_upload_speed, current_download_speed, mesh_collection
        )

        # Prepare recommendation response
        recommendation = {
            "current_position": current_position,
            "recommended_action": result['recommended_action'],
            "next_position": result['next_position'],
            "predicted_upload_speed": result['predicted_upload_speed'],
            "predicted_download_speed": result['predicted_download_speed']
        }

        return jsonify(recommendation), 200

    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error for debugging
        return jsonify({"error": "Server encountered an issue", "details": str(e)}), 500

# API endpoint to get a movement recommendation using DQN
@app.route('/get_dqn_recommendation', methods=['GET'])
def get_dqn_recommendation():
    try:
        # Fetch all mesh points from the database
        mesh_points = list(mesh_collection.find({}))
        if not mesh_points:
            return jsonify({"error": "No data available"}), 404

        # Assume the user's current position is the last recorded position
        current_point = mesh_points[-1]
        current_position = current_point['position']
        current_upload_speed = current_point['upload_speed']
        current_download_speed = current_point['download_speed']

        # Convert the current position to the required state format
        state = np.reshape(current_position, [1, state_size])

        # Use DQN agent to choose the next action
        action = dqn_agent.choose_action(state)

        # Define how the action affects movement
        next_position = current_position[:]
        if action == 0:  # Left
            next_position[0] -= 1
        elif action == 1:  # Right
            next_position[0] += 1
        elif action == 2:  # Up
            next_position[1] += 1
        elif action == 3:  # Down
            next_position[1] -= 1

        # Simulate next upload and download speeds (replace with actual logic if available)
        next_upload_speed = random.uniform(5, 50)
        next_download_speed = random.uniform(5, 50)

        # Store the transition in the agent's memory
        next_state = np.reshape(next_position, [1, state_size])
        dqn_agent.remember(state, action, next_download_speed, next_state, False)

        # Replay and train the agent
        dqn_agent.replay()

        recommendation = {
            "current_position": current_position,
            "recommended_action": ACTIONS[action],
            "next_position": next_position,
            "predicted_upload_speed": next_upload_speed,
            "predicted_download_speed": next_download_speed
        }

        return jsonify(recommendation), 200

    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error for debugging
        return jsonify({"error": "Server encountered an issue", "details": str(e)}), 500

# API endpoint to generate a heatmap
@app.route('/get_heatmap', methods=['GET'])
def get_heatmap():
    try:
        # Fetch all mesh points from the database
        mesh_points = list(mesh_collection.find({}))
        if not mesh_points:
            return jsonify({"error": "No data available"}), 404

        # Extract positions and signal strengths
        x = [point['position'][0] for point in mesh_points]
        y = [point['position'][1] for point in mesh_points]
        upload_speed = [point['upload_speed'] for point in mesh_points]
        download_speed = [point['download_speed'] for point in mesh_points]

        # Generate the heatmap based on upload and download speeds
        plt.figure(figsize=(6, 6))
        heatmap_upload, xedges, yedges = np.histogram2d(x, y, bins=(10, 10), weights=upload_speed, density=True)
        plt.imshow(heatmap_upload.T, origin='lower', cmap='hot', interpolation='nearest')
        plt.colorbar(label='Upload Speed (Mbps)')

        # Convert the heatmap plot to a base64 image string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_data_upload = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.clf()  # Clear the current figure

        # Generate heatmap for download speed
        plt.figure(figsize=(6, 6))
        heatmap_download, xedges, yedges = np.histogram2d(x, y, bins=(10, 10), weights=download_speed, density=True)
        plt.imshow(heatmap_download.T, origin='lower', cmap='hot', interpolation='nearest')
        plt.colorbar(label='Download Speed (Mbps)')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_data_download = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        return jsonify({
            "upload_heatmap_image": img_data_upload,
            "download_heatmap_image": img_data_download
        }), 200

    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error for debugging
        return jsonify({"error": "Server encountered an issue", "details": str(e)}), 500

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
