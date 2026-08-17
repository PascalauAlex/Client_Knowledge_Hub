import { useParams } from "react-router";
import { CardComponent } from "../../components/UI/CardComponent.tsx";
import { DefaultCard } from "../../components/UI/DefaultCard.tsx";
import { useGetClientDocuments } from "../../hooks/useDocuments.ts";
import { useGetClient } from "../../hooks/useClients.ts";

export const SingleClient = () => {
    const { id } = useParams<{ id: string }>();

    const { data: documents, isLoading, isError } = useGetClientDocuments(id);
    const { data: client, isLoading: isLoadingClient, isError: isErrorClient } = useGetClient(id);

    if (isLoadingClient) {
        return <div>Loading client details...</div>;
    }

    if (isErrorClient || !client) {
        return <div>An error occurred while loading the client.</div>;
    }

    return (
        <>
            <div className="flex flex-row gap-6 w-full items-start">

                <div className="w-1/3">
                    <CardComponent avatar={undefined} name={client.name} email={client.email}>
                        <div></div>
                    </CardComponent>
                </div>

                <div className="w-2/3">
                    <DefaultCard>
                        <div>
                            <h2>AI Summary</h2>
                            <h4>Document name: </h4>
                        </div>
                    </DefaultCard>
                </div>

            </div>

            <div className="flex-row max-w-1/2">
                <DefaultCard>
                    <div>
                        <h2 className="font-semibold text-green-600 text-lg">Documents</h2>

                        {isLoading && <p>Loading documents...</p>}
                        {isError && <p className="text-red-500">An error occurred while loading the documents.</p>}

                        <ul>
                            {documents && documents.length > 0 ? (
                                documents.map((doc) => (
                                    <li key={doc.id} className="py-2 border-b border-gray-100 last:border-0">
                                        <p className="font-medium text-white">{doc.name}{doc.extension_type}</p>
                                        <span className="text-sm text-gray-500">
                                            {new Date(doc.created_at).toLocaleDateString()}
                                        </span>

                                        {doc.file && (
                                            <a
                                                href={doc.file}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="ml-4 text-green-600 text-sm hover:underline"
                                            >
                                                Open
                                            </a>
                                        )}
                                        <span> | </span>
                                        <button className="text-green-600">Generate summary</button>
                                    </li>
                                ))
                            ) : (
                                !isLoading && <li>No documents for this current user.</li>
                            )}
                        </ul>
                    </div>
                </DefaultCard>
            </div>
        </>
    );
}