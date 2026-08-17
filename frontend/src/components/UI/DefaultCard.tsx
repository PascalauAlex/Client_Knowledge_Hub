import type {ReactNode} from "react";


export const DefaultCard = ({children} :{children:ReactNode} ) => {

    return(
        <div className="flex flex-col md:flex-row gap-6 p-4 w-full">
            <div
                className="flex-1 flex flex-col border border-slate-700 bg-slate-800 rounded-xl shadow-lg p-10 transition-colors text-slate-300">
                <div className="mb-8">
                    {children}
                </div>
            </div>
        </div>
    )
}