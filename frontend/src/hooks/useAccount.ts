import {useMutation, useQuery} from "@tanstack/react-query";
import {changePassword, getUserMe} from "../api/account.ts";



export const useGetUser = () =>{
    return useQuery({
        queryKey:["getUser"],
        queryFn:getUserMe
    })
}


export const useChangePassword = () =>{
    return useMutation({
        mutationFn: ({currentPassword,newPassword} : {currentPassword : string, newPassword : string}) =>
            changePassword(currentPassword,newPassword),
    })
}