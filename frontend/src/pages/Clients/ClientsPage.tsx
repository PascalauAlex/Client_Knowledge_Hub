import {useClients} from "../../hooks/useClients.ts";
import {ClientCard} from "../../components/clients/ClientCard.tsx";
import {useState} from "react";
import {CreateClient} from "../../components/clients/CreateClient.tsx";
import addUserIcon from "../../../public/add-user.png"
import {Modal} from "../../components/Modal.tsx";

export const ClientsPage = () => {
    const {data, isLoading, isError} = useClients()
    const [showModal, setShowModal] = useState(false)

    const toggleModal = () => {
        if (showModal) {
            setShowModal(false)
        } else {
            setShowModal(true)
        }

    }

    if (isLoading) return <div className="font-bold text-center text-2xl justify-center">Loading...</div>
    if (isError) return <p className="font-bold text-center text-2xl justify-center">Error while loading the resources, please try again</p>
    if (!data) return null

    return (
        <div>
            <div className="m-4 bg-slate-800 rounded-md p-4 text-slate-300 w-1/2">
                <button
                    onClick={() => toggleModal()}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 hover:border-slate-500 text-white font-semibold rounded-lg shadow-sm transition-all active:scale-95"
                >
                    <img src={addUserIcon} alt="Add Client" className="w-5 h-5 object-contain invert"/>
                    <span>Add client</span>
                </button>
            </div>
            <div className="m-10">
                <Modal isOpen={showModal} title="Create client" onClose={() => setShowModal(false)}>
                    <CreateClient onSuccess={() => setShowModal(false)}/>
                </Modal>
                <h1 className="font-bold ml-4 text-2xl">Clients</h1>
                {data.map((client) => (
                    <ClientCard key={client.id} client={client}/>
                ))}
            </div>
        </div>
    )
}