import { REVIEW_STATE } from "./reviewStateMapping";

export default function getCookie(name) {
    let cookieArray = document.cookie.split(";");
    //console.log(cookieArray)
    // Loop through the array elements
    for(let i = 0; i < cookieArray.length; i++) {
        let cookiePair = cookieArray[i].split("=");
        
        /* Removing whitespace at the beginning of the cookie name
        and compare it with the given string */
        if(name === cookiePair[0].trim()) {
            // Decode the cookie value and return
            //console.log("Found Cookie", cookiePair[1])
            return decodeURIComponent(cookiePair[1]);
        }
    }
    
    // Return null if not 
    console.log("Cookie not found")
    return null;
}

export function deleteCookie(name) {
    // Set the cookie to expire in the past, effectively deleting it
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/;`;
}

export function truncateString(str, maxLength = 35) {
    if (str.length > maxLength) {
        return str.slice(0, maxLength) + '...';
    }
    return str;
}

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
