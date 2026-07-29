import { useState} from "react";
import { useLogin} from "../../hooks/useAuth.ts";


export const LoginPage = () => {
    const [username,setUsername] = useState("")
    const [password,setPassword] = useState("")



    const loginMutation = useLogin()
    const handleSubmit = () => {
        loginMutation.mutate({username,password})
    }


    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-white shadow-md rounded-lg p-8">
                <h3 className="text-2xl font-semibold text-gray-900 text-center mb-6">
                    Log in
                </h3>

                <div className="flex flex-col gap-4">
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <input
                            value={username}
                            onChange={(e)=> setUsername(e.target.value)}
                            type="text"
                            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        />
                    </div>

                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Password</label>
                        <input
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            type="password"
                            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        />
                    </div>

                    <button
                        onClick={handleSubmit} disabled={loginMutation.isPending}
                        className="mt-2 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-md py-2 transition-colors">
                        {loginMutation.isPending ? "Logging in ..." : "Log in"}
                    </button>
                    {loginMutation.isError && (
                        <p className="text-red-500 text-sm">Incorrect email or password</p>
                    )}
                </div>
            </div>
        </div>
    )
}