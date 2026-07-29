import {fetchMe, type User} from "../api/auth.ts";
import { createContext, useContext } from "react";
import type {ReactNode} from "react";
import {useQuery, useQueryClient} from "@tanstack/react-query";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue{
    user: User | null;
    status : AuthStatus;
    setToken : (token: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProivder = ({children}:{children:ReactNode}) => {
    const queryClient = useQueryClient();

    const hasToken = Boolean(localStorage.getItem("token"));

    const {
        data: user,
        isLoading,
        isError,
    } = useQuery({
        queryKey:["me"],
        queryFn:fetchMe,
        enabled:hasToken, // without token -> query doesn't run
        retry: false,
        staleTime: 5 * 60 * 1000,

    });

    let status : AuthStatus;
    if(!hasToken){
        status= "unauthenticated";
    }else if(isLoading){
        status="loading"
    }else if (isError || !user){
        status = "unauthenticated"
    }else {
        status = "authenticated"
    }

    const setToken = (token : string) => {
        localStorage.setItem("token",token);
        queryClient.invalidateQueries({queryKey:["me"]});
    };

    const logout = () =>{
        localStorage.removeItem("token");
        queryClient.removeQueries({queryKey:["me"]});
        queryClient.clear();
    };

    return (
        <AuthContext.Provider
            value={{user:user?? null,status,setToken,logout}}>{children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if(!ctx) throw new Error("useAuth must be used with AuthProvider")
    return ctx;
}