import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    // 'Authorization': `Token ${localStorage.getItem('token')}` // Descomentar quando houver auth
  }
});

export default api;
