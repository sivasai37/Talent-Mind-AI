const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

const request = async (path, options = {}) => {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });
  if (!resp.ok) {
    const error = await resp.text();
    throw new Error(error || resp.statusText);
  }
  return resp.json();
};

export const analyzeJD = async (title, job_description) => {
  return request('/analyze-jd/', {
    method: 'POST',
    body: JSON.stringify({ title, job_description }),
  });
};

export const rankCandidates = async ({ job_title, job_description, ...rest }) => {
  return request('/rank/', {
    method: 'POST',
    body: JSON.stringify({ title: job_title, job_description, ...rest }),
  });
};

export const getCandidates = async () => {
  return request('/candidates/');
};

export const getRankings = async () => {
  return request('/rankings/');
};

export const exportRankings = () => {
  return `${API_BASE}/rankings/export/`;
};
