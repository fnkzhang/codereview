import "./Oauth.css"
import React, { useEffect, useState } from "react";
import { GoogleLogin } from "@react-oauth/google";

import { jwtDecode } from 'jwt-decode';
import getCookie from "../utils/utils";

export default function Oauth(){

    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [userData, setUserData] = useState(null)

    // Check If the user token is valid
    useEffect(() => {
        let credentialToken = getCookie("cr_id_token")
        if (credentialToken == null) {
            setIsLoggedIn(false)
            setUserData(null)
            return
        }

        let credentialObject = {
            "credential": credentialToken
        }

        verifyLogin(credentialObject)

    }, [])
    async function verifyLogin(credentialResponse) {
        let oAuthToken = getCookie("cr_id_token")
        let headers= {
            method: "POST",
            mode: "cors",
            headers: {
              "Authorization": oAuthToken,
              "Content-Type": "application/json"
            }
        }
        console.log("FETCHING")

        await fetch('/api/user/authenticate', headers)
        .then(response => response.json())
        .then(data => {
            if (data.success === false) {
                console.log("Failed to validate token")
                return
            }
            
            setUserData(data.body)
            console.log(data)
            setIsLoggedIn(true)
            // Save to Cookie
            document.cookie = `cr_id_token=${credentialResponse.credential}`;
        })
        .catch(e => console.log(e))

    }

    function DisplayLoginButton() {
        if (isLoggedIn) {
            return (<div className="Login-true">Logged IN to {userData.email}</div>)
        }

        return (
            <div>
        
            <GoogleLogin
                onSuccess={credentialResponse => {
                let decodedResponse = jwtDecode(credentialResponse.credential)
                console.log(decodedResponse)
                console.log(credentialResponse)
                
                verifyLogin(credentialResponse)
                
            }}
                onError={() => {console.log("Failed To login")}}
            />
        </div>
        )
    }

    return(
        <DisplayLoginButton/>
    )
}
