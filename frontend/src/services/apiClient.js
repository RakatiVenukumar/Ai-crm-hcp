import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'Unknown API error';
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (Array.isArray(detail)) {
        // Format FastAPI/Pydantic validation errors: "body.field_name: error message"
        message = detail
          .map((err) => {
            const field = err.loc ? err.loc.filter(l => l !== 'body').join('.') : 'field';
            return `${field}: ${err.msg}`;
          })
          .join('; ');
      } else if (typeof detail === 'string') {
        message = detail;
      } else {
        message = JSON.stringify(detail);
      }
    } else if (error?.response?.data?.error) {
      message = error.response.data.error;
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);
