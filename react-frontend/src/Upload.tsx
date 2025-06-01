import React, { useState } from 'react';
import axios from 'axios';

function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

 const handleUpload = async () => {
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  
  // Add the consent field here
  formData.append('consent', 'true');  // or 'yes', or a boolean as a string, depending on what API expects
  
  try {
    const response = await axios.post('http://localhost:8000/upload', formData);
    setSummary(response.data.summary);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};


  return (
    <div>
      <input type="file" onChange={handleFileChange} className="mb-4" />
      <button onClick={handleUpload} className="bg-blue-600 text-white px-4 py-2 rounded">Summarize</button>
      {summary && <div className="mt-6 bg-white p-4 rounded shadow">{summary}</div>}
    </div>
  );
}

export default Upload;
