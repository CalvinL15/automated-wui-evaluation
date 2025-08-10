import {Button} from '@mui/material';
import React from 'react';
import {useLocation} from "react-router-dom";

interface DownloadJsonButton {
  data: string;
}

const DownloadJsonButton = ({ data }: DownloadJsonButton) => {
  const location = useLocation();
  const { pathname } = location;
  // Function to handle the download
  const handleDownload = () => {
    const blob = new Blob([data], { type: 'application/json' });
    // Create a URL for the Blob
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${pathname.split("/").at(-1)}.json`;
    document.body.appendChild(link); // Required for Firefox
    link.click();
    document.body.removeChild(link); // Clean up
    URL.revokeObjectURL(url); // Free up memory allocated for the URL
  };

  return (
    <Button onClick={handleDownload}>
      Download JSON
    </Button>
  );
};

export default DownloadJsonButton;