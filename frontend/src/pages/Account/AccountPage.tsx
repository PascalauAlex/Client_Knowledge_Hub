import {useChangePassword, useGetUser} from "../../hooks/useAccount.ts";
import {useState} from "react";
import defaultAvatar from "/user.png"


export const AccountPage = () => {
    const {data, isLoading, isError} = useGetUser();
    const [currentPassword, setCurrentPassword] = useState("")
    const [newPassword, setNewPassword] = useState("")
    const changePassword = useChangePassword()
    if (isLoading) return <div className="font-bold text-center text-2xl justify-center">Loading...</div>
    if (isError) return <div className="font-bold text-center text-2xl">Error while loading the resources, please try
        again.</div>

    const handleSubmit = (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        changePassword.mutate({currentPassword, newPassword})
    }


    return (
        <div className="flex flex-col md:flex-row gap-6 p-4 w-full">

            {/* Card 1: Account Information */}
            <div
                className="flex-1 flex flex-col items-center justify-center border border-slate-700 bg-slate-800 rounded-xl shadow-lg p-10 transition-colors text-slate-300">
                <div className="mb-8 text-center">
                    <h1 className="font-bold text-xl text-emerald-600 hover:text-emerald-400 transition-colors">
                        Account information
                    </h1>
                </div>

                {/* Avatar */}
                <img
                    src={data?.image_file}
                    alt={defaultAvatar}
                    className="w-32 h-32 rounded-full object-cover object-top mb-4 shadow-md border-2 border-slate-700"
                />

                {/* Detalii Utilizator */}
                <div className="flex flex-col items-center gap-2 text-lg">
                 <span className="text-emerald-500 font-semibold text-2xl">
                 {data?.username}
                 </span>

                    <p className="text-slate-400">
                        Email: <span className="text-slate-300 font-normal">{data?.email}</span>
                    </p>
                </div>

            </div>

            {/* Card 2: Change Password */}
            <div
                className="flex-1 flex flex-col border border-slate-700 bg-slate-800 rounded-xl shadow-lg p-10 text-slate-300">
                <div className="text-center mb-6">
                    <h1 className="font-bold text-lg text-emerald-600 hover:text-emerald-400 transition-colors">
                        Change password
                    </h1>
                </div>


                <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1.5">
                            Current password
                        </label>
                        <input
                            type="password"
                            className="w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                            required
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1.5">
                            New password
                        </label>
                        <input
                            type="password"
                            className="w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                            required
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                        />
                    </div>

                    <div className="pt-2 flex justify-end">
                        <button
                            type="submit"
                            className="px-2 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold rounded-lg shadow-sm transition-all active:scale-95"
                        >
                            {changePassword.isPending ? "Updating..." : "Update password"}
                        </button>
                    </div>
                    <p className="text-red-500 font-semibold">{changePassword.isError && (changePassword.error?.message || "Error while changing the password!")}</p>

                </form>
            </div>

        </div>
    )
}