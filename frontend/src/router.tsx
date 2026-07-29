import {createBrowserRouter} from "react-router";
import Layout from "./components/layouts/Layout.tsx";
import {HomePage} from "./pages/Home/HomePage.tsx";
import {ClientsPage} from "./pages/Clients/ClientsPage.tsx";
import {DocumentsPage} from "./pages/Documents/DocumentsPage.tsx";
import {AccountPage} from "./pages/Account/AccountPage.tsx";
import {LoginPage} from "./pages/Auth/LoginPage.tsx";
import {SignUp} from "./pages/Auth/SignUp.tsx";
import {SingleClient} from "./pages/Clients/SingleClient.tsx";


export const router = createBrowserRouter([
    {
        path:"/",
        element: <Layout/>,
        children: [
            {index: true, element: <HomePage/>},
            {path:"/clients", element:<ClientsPage/>},
            {path:`/clients/:id`, element:<SingleClient/>},
            {path:"/documents",element:<DocumentsPage/>},
            {path:"/account",element:<AccountPage/>}
        ],
    },
    {
        path: "/login", element:<LoginPage/>,
    },
    {
        path:"/sign-up",element:<SignUp/>
    }
])