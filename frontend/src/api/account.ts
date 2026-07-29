import {api} from "./api.ts";

interface User{
    id:number
    username:string
    image_path:string,
    email:string,
    image_file : string
}



export const getUserMe = async () :Promise<User> =>{
    const response = await api.get("/api/users/me")

    return response.data
}

export const changePassword = async (currentPassword : string, newPassword: string) : Promise<string> =>{
    const formData = new FormData()
    formData.append("current_password",currentPassword)
    formData.append("new_password",newPassword)

    const response = await api.post("/api/users/me/password", formData)

    return response.data

}