import axios from 'axios';

// Use relative path — Vite proxies /api → http://localhost:5000/api
// This avoids all CORS issues entirely
const API_URL = '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadResumes = async (files, jobDescription) => {
  const formData = new FormData();
  files.forEach(file => formData.append('resumes', file));
  formData.append('job_description', jobDescription);

  const response = await axios.post(`${API_URL}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getCandidates = async () => {
  const response = await api.get('/candidates');
  return response.data;
};

export const shortlistCandidate = async (candidateId) => {
  const response = await api.post(`/shortlist/${candidateId}`);
  return response.data;
};

export const rejectCandidate = async (candidateId) => {
  const response = await api.post(`/reject/${candidateId}`);
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
