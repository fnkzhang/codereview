export default function getCookie(name) {
    let cookieArray = document.cookie.split(";");
    console.log(cookieArray)
    // Loop through the array elements
    for(let i = 0; i < cookieArray.length; i++) {
        let cookiePair = cookieArray[i].split("=");
        
        /* Removing whitespace at the beginning of the cookie name
        and compare it with the given string */
        if(name === cookiePair[0].trim()) {
            // Decode the cookie value and return
            console.log("Found Cookie", cookiePair[1])
            return decodeURIComponent(cookiePair[1]);
        }
    }
    
    // Return null if not 
    console.log("Cookie not found")
    return null;
}
