
import {DetailsButton} from "../UI/DetailsButton.tsx";
import {paths} from "../../paths.ts";
import type {Client} from "../../api/clients.ts";

interface ClientCardProps {
    client: Client
}


export const ClientCard = (props: ClientCardProps) => {
    return (

        <div className="w-full sm:w-1/2 md:w-1/3 p-2">


            <div className="flex flex-col justify-between h-full bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm hover:shadow-lg hover:-translate-y-1 hover:border-slate-600 transition-all duration-300">


                <div className="flex items-center gap-4 mb-4">


                    <div className="h-12 w-12 shrink-0 rounded-full bg-slate-700 flex items-center justify-center overflow-hidden border border-slate-600">
                        <img
                            src="/public/user.png"
                            className="h-full w-full object-cover p-2"
                            alt={`${props.client.name} avatar`}
                        />
                    </div>


                    <div className="overflow-hidden">
                        <h3 className="text-lg font-bold text-white truncate">
                            {props.client.name}
                        </h3>
                        <p className="text-sm text-slate-400 truncate">
                            {props.client.email}
                        </p>
                    </div>
                </div>


                <div className="mt-4 pt-4 border-t border-slate-700 flex justify-end">
                    <DetailsButton
                        to={paths.clientDetail(props.client.id)}
                        content="More"
                    />
                </div>

            </div>
        </div>
    )
}