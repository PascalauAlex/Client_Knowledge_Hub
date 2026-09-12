import { getAccessToken } from '@/utils/LocalStorageUtils.ts'


interface Config{
  authToken : string;
  backendUrl : string;
  maxFileSizeMB : number;
}

const config: Config = {
  authToken: getAccessToken(),
  backendUrl: 'https://localhost:8000',
  maxFileSizeMB: 5,
}

export default config;
