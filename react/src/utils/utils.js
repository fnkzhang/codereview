import { REVIEW_STATE } from "./reviewStateMapping";

/**
 *  Given a cookie name, decode and return the cookie contents.
 */
export default function getCookie(name) {
    let cookieArray = document.cookie.split(";");
    // Loop through the array elements
    for(let i = 0; i < cookieArray.length; i++) {
        let cookiePair = cookieArray[i].split("=");
        
        /* Removing whitespace at the beginning of the cookie name
        and compare it with the given string */
        if(name === cookiePair[0].trim()) {
            // Decode the cookie value and return
            return decodeURIComponent(cookiePair[1]);
        }
    }
    
    // Return null if no coolie found
    return null;
}

/**
 *  Given a cookie name, delete that cookie by setting its expiration date to the past.
 */
export function deleteCookie(name) {
    // Set the cookie to expire in the past, effectively deleting it
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/;`;
}

/**
 *  Given a string, truncate it to some given length, or 35 characters if unspecified.
 */
export function truncateString(str, maxLength = 35) {
    if (str.length > maxLength) {
        return str.slice(0, maxLength) + '...';
    }
    return str;
}

/**
 *  Given a review state, provide the appropriate text styling to display it.
 */
export function getColor ( state ) {
    let stateColor = 'text-textcolor';

    if (state === REVIEW_STATE.OPEN)
        stateColor = 'text-reviewOpen'
    else if (state === REVIEW_STATE.REVIEWED)
        stateColor = 'text-reviewReviewed'
    else if (state === REVIEW_STATE.APPROVED)
        stateColor = 'text-reviewApproved'
    else
        stateColor = 'text-reviewClosed'

    return stateColor
}
