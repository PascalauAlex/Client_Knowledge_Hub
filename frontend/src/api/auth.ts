import {api} from "./api.ts";

export interface User{
    id: string,
    email : string,
    username : string
}



export const login = async (username: string, password: string): Promise<string> =>{
    // OAuth2PasswordRequestForm expects form-encoded, not JSON
    const form = new URLSearchParams()
    form.append("username",username)
    form.append("password",password)

    const response = await api.post("/api/users/token",form, {
        headers: {"Content-type":"application/x-www-form-urlencoded"},
    } )

    return response.data.access_token
}

export const signup = async (username: string, password: string, email: string) : Promise<string> =>{
    const form = new FormData()
    form.append("username",username.toLowerCase())
    form.append("password",password)
    form.append("email",email.toLowerCase())

    const response = await api.post("/api/users", form)

    return response.data
}

export const logout = () : string => {
    const token = localStorage.getItem("token")
    if(token){
        localStorage.removeItem("token")
    }
    return "Log out successfully!"
}

export async function fetchMe(): Promise<User>{
    const {data}  = await api.get<User>("/api/users/me")

    return data
}

