import axios, { type InternalAxiosRequestConfig } from 'axios'
import { getAccessToken } from '@/utils/LocalStorageUtils.ts'

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout:5000,
});

api.interceptors.request.use((config  )   => {
  const token : string = getAccessToken();
  if(token){
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config
})








export default api
