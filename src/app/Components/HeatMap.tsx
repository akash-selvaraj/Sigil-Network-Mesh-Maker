'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Image from 'next/image';
const HeatMap: React.FC = () => {
  const [uploadHeatmap, setUploadHeatmap] = useState<string>('');
  const [downloadHeatmap, setDownloadHeatmap] = useState<string>('');

  const fetchHeatmap = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_heatmap');
      setUploadHeatmap(response.data.upload_heatmap_image);
      setDownloadHeatmap(response.data.download_heatmap_image);
    } catch (error) {
      console.error('Error fetching heatmap:', error);
    }
  };

  useEffect(() => {
    fetchHeatmap();
    const interval = setInterval(fetchHeatmap, 5000); // Fetch heatmap every 5 seconds
    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-2xl font-semibold mb-2">Upload Speed</h3>
          {uploadHeatmap ? (
            <Image
              src={`data:image/png;base64,${uploadHeatmap}`}
              alt="Upload Heatmap"
              className="w-full h-auto rounded"
              width={100}
              height={100}
            />
          ) : (
            <p className="text-gray-500">Loading upload heatmap...</p>
          )}
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-2xl font-semibold mb-2">Download Speed</h3>
          {downloadHeatmap ? (
            <Image
              src={`data:image/png;base64,${downloadHeatmap}`}
              alt="Download Heatmap"
              className="w-full h-auto rounded"
              width={100}
              height={100}
            />
          ) : (
            <p className="text-gray-500">Loading download heatmap...</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default HeatMap;
