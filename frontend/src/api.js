// api.js — HireGenius AI API Client

export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

const request = async (path, options = {}) => {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  if (!resp.ok) {
    let errorMsg = resp.statusText;
    try {
      const errorData = await resp.json();
      errorMsg = errorData.detail || errorData.error || JSON.stringify(errorData);
    } catch {
      errorMsg = await resp.text().catch(() => resp.statusText);
    }
    throw new Error(errorMsg || `HTTP ${resp.status}`);
  }
  return resp.json();
};

export const analyzeJD = async (title, job_description) => {
  return request('/analyze-jd/', {
    method: 'POST',
    body: JSON.stringify({ title, job_description }),
  });
};

export const rankCandidates = async ({ job_title, job_description, top_k = 10, ...rest }) => {
  return request('/rank/', {
    method: 'POST',
    body: JSON.stringify({ title: job_title, job_description, top_k, ...rest }),
  });
};

export const getCandidates = async () => {
  return request('/candidates/');
};

export const getRankings = async () => {
  return request('/rankings/');
};

export const getRankingDetail = async (id) => {
  return request(`/rankings/${id}/`);
};

export const getDashboardStats = async () => {
  return request('/stats/');
};

export const getTalentInsights = async (job_description = '', role_type = 'general') => {
  return request('/talent-insights/', {
    method: 'POST',
    body: JSON.stringify({ job_description, role_type }),
  });
};

export const exportRankingsUrl = (jobId, format = 'full') => {
  const params = new URLSearchParams();
  if (jobId) params.set('job_id', jobId);
  if (format) params.set('format', format);
  return `${API_BASE}/rankings/export/?${params.toString()}`;
};
