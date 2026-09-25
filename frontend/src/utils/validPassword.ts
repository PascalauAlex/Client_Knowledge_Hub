interface ValidPassword{
  valid : boolean
  errorMessage? : string
}

export function isValidPassword(password : string): ValidPassword {
  const validPassword : ValidPassword = {
    valid: false,
    errorMessage: ''
  }
  if(password.length < 10){
    validPassword.errorMessage = "Password is too short. The length has to be 10 or more characters."
    return validPassword
  }
  if(!/[a-z]/.test(password)){
    validPassword.errorMessage = "The password must contain at least one lowercase letter."
  }
  if(!/[A-Z]/.test(password)){
    validPassword.errorMessage = 'The password must contain at least one uppercase letter.'
  }
  if(!/[0-9]/.test(password)){
    validPassword.errorMessage = 'The password must contain at least one digit.'
  }
  if (!/[^a-zA-Z0-9]/.test(password)){
    validPassword.errorMessage = 'The password must contain at least one special character.'
  }

  validPassword.valid = true
  return validPassword

}
