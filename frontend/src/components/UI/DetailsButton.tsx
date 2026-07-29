import {Link} from "react-router";

interface DetailsButtonProps {
    to : string,
    content : string

}


export const DetailsButton = ({to, content} : DetailsButtonProps) =>{
    return(
        <Link
            className="bg-emerald-700 border-emerald-700 text-white p-2 rounded-md hover:bg-emerald-500"
            to={to}>{content}</Link>
    )
}