import { useMutation, useQuery } from "@tanstack/react-query"
import {createClient, getClients, getClient} from "../api/clients.ts";



export const useClients = () =>{
    return useQuery({
        queryFn:getClients,
        queryKey:["clients"]
    })
}

export const useCreateClient = () =>{
    return useMutation({
        mutationFn: ({name,email} : {name : string, email : string}) =>
            createClient(name,email),
    })
}

export const useGetClient= (client_id: string | number) =>{
    return useQuery({
        queryFn: () => getClient(client_id),
        queryKey:["singleClient"]
    })
}


