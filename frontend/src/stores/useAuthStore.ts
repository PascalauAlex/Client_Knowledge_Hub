import {create} from 'zustand'
import {persist, createJSONStorage} from "zustand/middleware";


interface User{
    username : string
}

export interface AuthState{
    user: User | null,
    token : string | null,
    isAuthenticated : boolean;
    login : (userData : User, token: string) => void,
    logout : () => void;
}


export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,

            login: (userData : User, token : string) =>
                set({
                    user: userData,
                    token: token,
                    isAuthenticated: true
                }),

            logout: () =>
                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                }),
        }),
        {
            name: 'auth-storage', // key name saved in localstorage
            storage: createJSONStorage(() => localStorage),

        }
    )
);