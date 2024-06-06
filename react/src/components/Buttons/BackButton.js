import React from "react";
import { useNavigate } from "react-router-dom";

/**
 * Component for a back button that navigates to a specified location.
 *
 * @component
 * @example
 * // Example usage:
 * <BackButton location="/dashboard" />
 *
 * @param {object} props - Component props
 * @param {string} props.location - The location to navigate to when the button is clicked
 */
export default function BackButton( props ) {

    const navigate = useNavigate()

    /**
     * Handles the click event of the button by navigating to the specified location.
     */
    const handleClick = () => {
        navigate(props.location);
    }

    return <button onClick={handleClick}
    className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1 text-textcolor text-xl">
        Return
    </button>
}