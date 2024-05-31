import React from "react";
import { useNavigate } from "react-router-dom";

export default function BackButton( props ) {
    const navigate = useNavigate()

    const handleClick = () => {
        navigate(props.location);
    }
    return <button onClick={handleClick}
    className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1 text-textcolor text-xl">
        Return
    </button>
}