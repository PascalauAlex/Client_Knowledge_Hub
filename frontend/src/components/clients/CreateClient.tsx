import {useState} from "react";
import {useCreateClient} from "../../hooks/useClients.ts";

interface CreateClientFormProps{
    onSuccess : () =>void;
}



export const CreateClient = ({onSuccess} : CreateClientFormProps) => {
    const [name,setName] = useState('')
    const [email,setEmail] = useState('')
    const createClientHook = useCreateClient()
    const handleSubmit = (e : React.SubmitEvent<HTMLFormElement>) =>{
        e.preventDefault()
        createClientHook.mutate({name,email})
        onSuccess();
    }

    return(
        <div>
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">
                        Name
                    </label>
                    <input
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        type="text"
                        placeholder="John Doe"
                        className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">
                        Email
                    </label>
                    <input
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        type="email"
                        placeholder="john@example.com"
                        className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                        required
                    />
                </div>
                <div className="pt-2 flex justify-end">

                     <button
                        type="submit"
                        className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold rounded-lg shadow-sm transition-all active:scale-95"
                    >
                         {createClientHook.isPending ? "Creating..." : "Create" }
                    </button>
                </div>

            </form>
        </div>
    )
}