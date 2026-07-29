

export const paths = {
    clients: () => "/clients",
    clientDetail: (id: number | string) => `/clients/${id}`,
    documents : () => '/documents',
    account : () => "/account",
    login : () => "/login",
    signup : () => "/sign-up"
}