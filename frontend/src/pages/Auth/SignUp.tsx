import { useState } from "react";
import { useSignUp } from "../../hooks/useAuth.ts";

export const SignUp = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");

    const signupMutation = useSignUp();


    const handleSubmit = () => {
        signupMutation.mutate({ username, password, email });
    };


    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-white shadow-md rounded-lg p-8">
                <h3 className="text-2xl font-semibold text-gray-900 text-center mb-6">
                    Sign up
                </h3>
                <div className="flex flex-col gap-4">
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <input
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            type="text"
                            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        />
                    </div>

                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Username</label>
                        <input
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
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
                        onClick={handleSubmit}
                        disabled={signupMutation.isPending}
                        className="mt-2 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-md py-2 transition-colors"
                    >
                        {signupMutation.isPending ? "Signing up ..." : "Sign up"}
                    </button>

                    {signupMutation.isError && (
                        <p className="text-red-500 text-sm">Something went wrong. Try again.</p>
                    )}
                </div>
            </div>
        </div>
    );
};