import {api} from "./api.ts";


export interface Documents{
    id: number,
    name : string,
    file: string,
    client_id : number,
    created_at : string
    extension_type : string
}


export const getClientDocuments = async (client_id: string | number): Promise<Documents[]> => {
    const response = await api.get(`/api/clients/documents/${client_id}`);
    return response.data;
}