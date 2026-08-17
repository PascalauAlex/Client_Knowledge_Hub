import {useQuery} from "@tanstack/react-query";
import {getClientDocuments} from "../api/documents.ts";


export const useGetClientDocuments = (id: string | undefined) => {
    return useQuery({

        queryKey: ["client_documents", id],
        queryFn: () => getClientDocuments(id as string),
        enabled: !!id
    });
}