
import type {ReactNode} from "react";
import defaultAvatar from "/user.png"

interface CardComponentI{
    avatar :  string | undefined
    name : string
    email : string
    children : ReactNode
}


export const CardComponent = ({name, avatar, email, children} : CardComponentI) =>{
    return(
        <div className="flex flex-col md:flex-row gap-6 p-4 w-full">
            <div
                className="flex-1 flex flex-col items-center justify-center border border-slate-700 bg-slate-800 rounded-xl shadow-lg p-10 transition-colors text-slate-300">
                <div className="mb-8 text-center">
                    <h1 className="font-bold text-xl text-emerald-600 hover:text-emerald-400 transition-colors">
                        {name}
                    </h1>
                </div>

                {/* Avatar */}
                <img
                    src={avatar}
                    alt={defaultAvatar}
                    className="w-32 h-32 rounded-full object-cover object-top mb-4 shadow-md border-2 border-slate-700"
                />

                {/* Detalii Utilizator */}
                <div className="flex flex-col items-center gap-2 text-lg">
                 <span className="text-emerald-500 font-semibold text-2xl">
                 {}
                 </span>

                    <p className="text-slate-400">
                        Email: <span className="text-slate-300 font-normal">{email}</span>
                    </p>
                </div>
                <div>
                    {children}
                </div>

            </div>
        </div>
    )
}