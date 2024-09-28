'use client';

import React, { useEffect, useState, useCallback } from 'react';
import SubmitData from './Components/SubmitData';
import Heatmap from './Components/HeatMap';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Define types for the fetched data
interface QLearningRecommendation {
  recommended_action: string;
  
  current_position: number[];  // current position will be fetched
  next_position: number[];     // next recommended position
}

interface DQNRecommendation extends QLearningRecommendation {
  predicted_download_speed: number;
  predicted_upload_speed: number;
}

const Home: React.FC = () => {
  const [algorithm, setAlgorithm] = useState<'Q-learning' | 'DQN'>('Q-learning'); // State to manage selected algorithm
  const [currentPosition, setCurrentPosition] = useState<number[]>([0, 0]); // State to manage the current position
// Log the recommended action if you need to track it or debug

  // Memoize the fetchRecommendation function
  const fetchRecommendation = useCallback(async () => {
    try {
      const endpoint = algorithm === 'Q-learning' 
        ? 'http://localhost:5000/get_q_learning_recommendation'
        : 'http://localhost:5000/get_dqn_recommendation';

      const response = await axios.get<QLearningRecommendation | DQNRecommendation>(endpoint);

      if (response.data && response.data.recommended_action) {
        const { recommended_action, next_position } = response.data;
        console.log('Recommended action:', recommended_action);
        // Get movement instructions
        const moveInstructions = getMovementInstructions(currentPosition, next_position);

        // Display appropriate toast notification based on the selected algorithm
        if (algorithm === 'Q-learning') {
          toast.info(
            <div style={{ lineHeight: '1.5' }}>
              <p><strong>Q-Learning:</strong> {moveInstructions}</p>
              <p><strong>Next Position:</strong> {next_position.join(', ')}</p>
            </div>,
            { position: 'bottom-left', autoClose: 5000 }
          );
        } else {
          const { predicted_download_speed, predicted_upload_speed } = response.data as DQNRecommendation;
          toast.success(
            <div style={{ lineHeight: '1.5' }}>
              <p><strong>DQN:</strong> {moveInstructions}</p>
              <p><strong>Next Position:</strong> {next_position.join(', ')}</p>
              <p><strong>Predicted Download Speed:</strong> {predicted_download_speed.toFixed(2)} Mbps</p>
              <p><strong>Predicted Upload Speed:</strong> {predicted_upload_speed.toFixed(2)} Mbps</p>
            </div>, 
            { position: 'bottom-right', autoClose: 5000 }
          );
        }

        // Update the current position state after the recommendation
        setCurrentPosition(next_position);

      } else {
        console.warn('Unexpected response structure:', response.data);
      }
    } catch (error) {
      console.error('Error fetching recommendation:', error);
      toast.error('Error fetching recommendation. Please try again later.', {
        position: 'bottom-right',
        autoClose: 5000,
      });
    }
  }, [algorithm, currentPosition]);  // Add algorithm and currentPosition as dependencies

  // Function to get movement instructions based on current and next positions
  const getMovementInstructions = (current_position: number[], next_position: number[]): string => {
    const xDiff = next_position[0] - current_position[0];
    const yDiff = next_position[1] - current_position[1];
    
    const instructions: string[] = [];

    // Calculate horizontal movement
    if (xDiff > 0) {
      instructions.push(`Move right ${xDiff} meters`);
    } else if (xDiff < 0) {
      instructions.push(`Move left ${Math.abs(xDiff)} meters`);
    }

    // Calculate vertical movement
    if (yDiff > 0) {
      instructions.push(`Move forward ${yDiff} meters`);
    } else if (yDiff < 0) {
      instructions.push(`Move backward ${Math.abs(yDiff)} meters`);
    }

    return instructions.length > 0 ? instructions.join(', ') : 'No movement needed';
  };

  useEffect(() => {
    // Fetch recommendations periodically based on the selected algorithm
    const interval = setInterval(fetchRecommendation, 10000); // every 10 seconds

    return () => {
      clearInterval(interval); // Cleanup interval on component unmount
    };
  }, [fetchRecommendation]);  // Dependency on the memoized fetchRecommendation function

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">

      {/* Navbar with header and algorithm selector */}
      <nav className="w-full bg-blue-500 p-4 text-white flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Sigil Network Mesh Maker</h1>
        
        <div className="flex items-center">
          <label className="mr-2">Select Algorithm:</label>
          <select 
            value={algorithm} 
            onChange={(e) => setAlgorithm(e.target.value as 'Q-learning' | 'DQN')}
            className="border p-2 rounded text-black"
          >
            <option value="Q-learning">Q-learning</option>
            <option value="DQN">DQN</option>
          </select>
        </div>
      </nav>

      {/* Flex container for side-by-side layout */}
      <div className="flex flex-col md:flex-row w-full max-w-7xl flex-grow min-h-full">
        <div className="flex-1 p-2 min-h-full flex flex-col">
          <SubmitData />
        </div>
        <div className="flex-1 p-2 min-h-full flex flex-col">
          <Heatmap />
        </div>
      </div>

      {/* Toast container to display toast notifications */}
      <ToastContainer />
    </div>
  );
};

export default Home;
