import {Link, useNavigate} from "react-router";

import {paths} from "../../paths.ts";
import {useAuthStore} from "../../stores/useAuthStore.ts";




const Header = () => {
    const { user, isAuthenticated, logout } = useAuthStore();
    const navigate = useNavigate()
    const handleLoggout = async ()=>{
         logout();
         navigate("/")
    }

    return (
        <header className="mx-4 mt-4 mb-6 bg-slate-800 border border-slate-700 rounded-xl shadow-sm text-white">
            <div className="flex items-center justify-between px-6 py-4">
                <Link
                    to="/"
                    className="text-xl md:text-2xl font-bold tracking-wide text-white hover:text-emerald-400 transition-colors"
                >
                    Client Knowledge Hub
                </Link>
                <nav className="flex items-center text-base font-medium">
                    {isAuthenticated ? (
                        <div className="flex items-center gap-4 md:gap-6">

                            <Link
                                to="/clients"
                                className="text-slate-300 hover:text-emerald-400 transition-colors"
                            >
                                Clients
                            </Link>

                            <Link
                                to="/documents"
                                className="text-slate-300 hover:text-emerald-400 transition-colors"
                            >
                                Documents
                            </Link>

                            <div className="hidden md:block h-6 w-px bg-slate-700"></div>

                            <Link
                                to="/account"
                                className="flex items-center gap-2 text-white hover:text-emerald-400 transition-colors"
                            >
                                <div className="h-7 w-7 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center overflow-hidden">
                                    <img src="/public/user.png" alt="user" className="h-full w-full object-cover p-1" />
                                </div>
                                <span>{user ? user.username : "Account"}</span>
                            </Link>

                            <button
                                type="button"
                                className="text-sm px-4 py-2 rounded-lg font-semibold text-emerald-400 border border-emerald-400/30 hover:border-emerald-400 hover:bg-emerald-400/10 transition-all"
                                onClick={() => handleLoggout()}
                            >
                                Log out
                            </button>

                        </div>
                    ) : (
                        <div className="flex items-center gap-4 md:gap-6">
                            <Link
                                to={paths.login()}
                                className="text-slate-300 hover:text-white transition-colors"
                            >
                                Login
                            </Link>

                            <Link
                                to={paths.signup()}
                                className="bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold px-5 py-2 rounded-lg transition-colors shadow-sm"
                            >
                                Sign up
                            </Link>
                        </div>
                    )}
                </nav>

            </div>
        </header>
    )
}

export default Header