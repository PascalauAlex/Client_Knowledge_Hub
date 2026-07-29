import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "react-router"
import {login, signup} from "../api/auth"
import {useAuthStore} from "../stores/useAuthStore.ts";





export const useLogin = () => {
    const navigate = useNavigate();
    const loginUser = useAuthStore((state) => state.login);

    return useMutation({
        mutationFn: ({username, password} : {username: string, password: string}) =>
            login(username, password),

        onSuccess: (token: string, variables) => {
            loginUser({ username: variables.username }, token);
            navigate("/");
        },
    })
}



export const useSignUp = () =>{
    const navigate = useNavigate()

    return useMutation({
        mutationFn:({username,password,email} : {username:string, password:string, email:string}) =>
            signup(username,password,email),
        onSuccess: () =>{
            navigate('/log-in')
        }
    })
}


