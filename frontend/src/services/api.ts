import axios from 'axios';
import { supabase } from './supabase';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use(async (config) => {
  // Se a rota for de login ou já tiver header manual, não consulta o Supabase
  if (config.headers.Authorization) {
    return config;
  }

  const { data } = await supabase.auth.getSession();
  if (data?.session?.access_token) {
    config.headers.Authorization = `Bearer ${data.session.access_token}`;
  }
  
  return config;
}, (error) => Promise.reject(error));

export default api;