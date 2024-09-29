'use client';

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const SubmitData: React.FC = () => {
  const [position, setPosition] = useState<[number, number]>([0, 0]);
  const [uploadSpeed, setUploadSpeed] = useState<number>(0);
  const [downloadSpeed, setDownloadSpeed] = useState<number>(0);
  const [timestamp, setTimestamp] = useState<string | null>(null);
  const uploadSpeedRef = useRef<number>(0); // Store the latest upload speed
  const downloadSpeedRef = useRef<number>(0); // Store the latest download speed

  // Function to get user's geolocation
  const getPosition = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords;
          setPosition([latitude, longitude]);
        },
        (err) => {
          console.error('Error getting geolocation:', err);
        }
      );
    }
  };

  // Function to test network speed (both upload and download)
  const getNetworkSpeed = () => {
    // Download speed measurement
    const downloadStartTime = performance.now();
    const downloadUrl = 'https://httpbin.org/image/jpeg'; // Use httpbin for download speed testing

    // Create a new image to measure download speed
    const downloadImage = new Image();
    downloadImage.src = downloadUrl;

    downloadImage.onload = () => {
      const downloadEndTime = performance.now();
      const downloadDuration = (downloadEndTime - downloadStartTime) / 1000; // in seconds
      const downloadSpeedMbps = (1 * 8) / downloadDuration; // 1MB file size assumed for speed calculation
      downloadSpeedRef.current = downloadSpeedMbps; // Update the reference
      setDownloadSpeed(downloadSpeedMbps); // Set state
    };

    // Upload speed measurement
    const uploadData = new Blob([new Uint8Array(1000000)]); // 1 MB Blob for upload
    const xhrUpload = new XMLHttpRequest();
    const uploadUrl = 'https://httpbin.org/post'; // Use httpbin for upload testing

    xhrUpload.open('POST', uploadUrl, true);

    xhrUpload.onloadstart = () => {
      const uploadStartTime = performance.now();

      // Track upload progress
      xhrUpload.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const uploadedBytes = event.loaded; // Number of bytes uploaded
          const uploadDuration = (performance.now() - uploadStartTime) / 1000; // in seconds

          if (uploadDuration > 0) {
            // Calculate upload speed in Mbps
            const uploadSpeedMbps = (uploadedBytes * 8) / (uploadDuration * 1e6); // in Mbps
            uploadSpeedRef.current = uploadSpeedMbps; // Update the reference
            setUploadSpeed(uploadSpeedMbps); // Set state
          }
        }
      };

      // Handle the completion of the upload
      xhrUpload.onload = () => {
        if (xhrUpload.status === 200) {
          console.log('Upload successful:', xhrUpload.responseText);
        } else {
          console.error('Upload failed:', xhrUpload.statusText);
        }
      };
    };

    // Start the upload
    xhrUpload.send(uploadData);
  };

  // Periodically update the frontend with the latest speed
  useEffect(() => {
    const interval = setInterval(() => {
      setUploadSpeed(uploadSpeedRef.current); // Update UI with the latest upload speed
      setDownloadSpeed(downloadSpeedRef.current); // Update UI with the latest download speed
    }, 1000); // Update every second

    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  useEffect(() => {
    getPosition();
    getNetworkSpeed();
    setTimestamp(new Date().toISOString());
  }, []);

  const submitData = async () => {
    // Create the data object according to the specified structure
    const data = {
      position: position, // Use the latitude and longitude directly
      upload_speed: uploadSpeed,
      download_speed: downloadSpeed,
      timestamp: timestamp,
    };

    try {
      const response = await axios.post('http://localhost:5000/submit_data', data);
      if (response.status === 200) {
        console.log('Data submitted successfully!');
      } else {
        console.error('Failed to submit data.');
      }
    } catch (error) {
      console.error('Error submitting data:', error);
    }
  };

  // Automatically submit data every 30 seconds
  useEffect(() => {
    const submitInterval = setInterval(() => {
      setTimestamp(new Date().toISOString()); // Update timestamp
      submitData(); // Submit data automatically
    }, 30000); // 30 seconds interval

    return () => clearInterval(submitInterval); // Cleanup on component unmount
  }, [position, uploadSpeed, downloadSpeed, timestamp]);

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center mb-4">Submit Signal Data</h2>
      <p className="text-lg">Position: {`Latitude: ${position[0]}, Longitude: ${position[1]}`}</p>
      <p className="text-lg">Upload Speed: {uploadSpeed.toFixed(2)} Mbps</p>
      <p className="text-lg">Download Speed: {downloadSpeed.toFixed(2)} Mbps</p>
      <p className="text-lg">Timestamp: {timestamp}</p>
    </div>
  );
};

export default SubmitData;
