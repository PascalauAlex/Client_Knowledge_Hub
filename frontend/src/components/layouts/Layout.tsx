import Header from "./Header.tsx";
import {Outlet} from "react-router";
import Footer from "./Footer.tsx";


const Layout = () =>{
    return(
        <div className="flex min-h-screen flex-col bg-slate-300">
            <Header/>
            <main className="flex-1 ">
                <Outlet/>
            </main>


            <Footer/>

        </div>
    )
}

export default Layout