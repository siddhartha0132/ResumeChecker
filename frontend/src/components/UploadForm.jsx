import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = '/api'; // Vite proxies /api → localhost:5000, no CORS needed

export default function UploadForm({ onUploadComplete, setLoading }) {
  const [files, setFiles] = useState([]);
  const [jobDescription, setJobDescription] = useState('');
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 20,
  });

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (files.length === 0) { toast.error('Please select at least one resume'); return; }
    if (!jobDescription.trim()) { toast.error('Please enter a job description'); return; }

    setUploading(true);
    setLoading(true);

    const formData = new FormData();
    files.forEach(file => formData.append('resumes', file));
    formData.append('job_description', jobDescription);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      if (response.data.success) {
        onUploadComplete(response.data);
        setFiles([]);
        setJobDescription('');
      } else {
        toast.error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(`Error: ${error.response?.data?.error || error.message || 'Failed to connect to backend'}`);
    } finally {
      setUploading(false);
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <span>📄</span> Upload Resumes
      </h2>

      {/* Dropzone — only the drop area has getRootProps, NOT the whole form */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-green-400 bg-green-500/10'
            : 'border-white/15 hover:border-green-500/50 hover:bg-green-500/5'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-4xl mb-2">📁</div>
        {isDragActive ? (
          <p className="text-green-400 font-semibold">Drop the PDF files here…</p>
        ) : (
          <p className="text-gray-400">Drag & drop resumes here, or click to select</p>
        )}
        <p className="text-xs text-gray-600 mt-2">Supports PDF files (text and scanned) · Max 20 files</p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-semibold text-gray-300 mb-2">
            Selected Files ({files.length})
          </p>
          <div className="max-h-36 overflow-y-auto rounded-xl p-2 space-y-1" style={{ background: 'rgba(0,0,0,0.3)' }}>
            {files.map((file, index) => (
              <div key={index} className="flex justify-between items-center py-1.5 px-3 rounded-lg hover:bg-white/5">
                <span className="text-sm text-gray-300 truncate">📄 {file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-400 hover:text-red-300 text-xs ml-2 flex-shrink-0"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Job Description */}
      <div className="mt-5">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          📝 Job Description
        </label>
        <textarea
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the job description here. This will be used to rank candidates based on skill match…"
          className="w-full p-3 h-36 resize-none text-sm"
          style={{
            background: 'rgba(0,0,0,0.4)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            color: 'white',
          }}
        />
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={uploading || files.length === 0}
        className="btn-primary w-full mt-5 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {uploading ? (
          <span className="flex items-center justify-center gap-2">
            <div className="animate-spin h-4 w-4 border-2 border-black/30 border-t-black rounded-full" />
            Processing…
          </span>
        ) : (
          '🔍 Analyze & Rank Candidates'
        )}
      </button>
    </div>
  );
}
