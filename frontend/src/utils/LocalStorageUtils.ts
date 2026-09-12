


export function setAccessToken (access_token : string) : void {
  if (!access_token){
    return
  }
  localStorage.setItem("access_token",access_token)
}

export function getAccessToken(): string{
  const token : string | null = localStorage.getItem("access_token");
  if (!token){
    return ""
  }
  return token
}

export function deleteAccessToken(){
  localStorage.removeItem("access_token")
}

