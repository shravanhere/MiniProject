import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    return Promise.resolve();
  },
  getCurrentUser: () => api.get('/auth/me'),
};

// Image Upload API
export const imageAPI = {
  upload: (formData, onProgress) => 
    api.post('/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    }),
  getAll: () => api.get('/images'),
  getById: (id) => api.get(`/images/${id}`),
  delete: (id) => api.delete(`/images/${id}`),
};

// Detection API
export const detectionAPI = {
  runDetection: (imageId) => api.post('/detection/run', { imageId }),
  getResults: (detectionId) => api.get(`/detection/results/${detectionId}`),
  getAllDetections: () => api.get('/detection/all'),
  getStats: () => api.get('/detection/stats'),
};

// Encroachment API
export const encroachmentAPI = {
  getAll: (params) => api.get('/encroachments', { params }),
  getById: (id) => api.get(`/encroachments/${id}`),
  verify: (id, status, remarks) => 
    api.put(`/encroachments/${id}/verify`, { status, remarks }),
  getReport: (id) => api.get(`/encroachments/${id}/report`, {
    responseType: 'blob',
  }),
  getStatistics: () => api.get('/encroachments/statistics'),
};

// Map API
export const mapAPI = {
  getLandBoundaries: (bounds) => api.get('/map/boundaries', { params: bounds }),
  getPublicLands: () => api.get('/map/public-lands'),
};

export default api;
