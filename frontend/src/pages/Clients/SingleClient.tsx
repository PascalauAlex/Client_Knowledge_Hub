import {CardComponent} from "../../components/UI/CardComponent.tsx";


export const SingleClient = () =>{
    return (
        <>
        <div>
            <CardComponent avatar={undefined} name={"Ioan"} email={"pascalau@alex.com"}>
                <div>
                    <p>Ceva</p>
                </div>
            </CardComponent>
        </div>
        </>
    )
}