import axios from "axios"



export const api  = axios.create({
    baseURL : "http://localhost:8000",
    headers:{
        "Content-type":"application/json"
    }
})

api.interceptors.request.use((config ) => {
    const storageString : string | null = localStorage.getItem("auth-storage")

    let token = null;
    if (storageString){
        const storageObject  = JSON.parse(storageString);
        token = storageObject.state.token
    }

    if (token){
        config.headers.Authorization = `bearer ${token}`
    }
    return config
})

