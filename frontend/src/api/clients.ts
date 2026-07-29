import {api} from "./api.ts";



export interface Client{
    id : number,
    name : string,
    email : string,
    created_at : string
}




export const getClients = async () : Promise<Client[]> =>{
    const response = await api.get("/api/clients")

    return response.data
}

export const createClient = async (name: string, email:string) : Promise<Client> =>{
    const formData = new FormData()
    formData.append("name",name)
    formData.append("email",email)

    const response = await api.post("/api/clients", formData)

    return response.data
}

export const getClient = async (client_id : number | string) : Promise<Client> =>{
    const response = await api.get(`/api/clients/${client_id}`)

    return response.data
}