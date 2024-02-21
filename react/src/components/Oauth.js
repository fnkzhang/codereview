import React, { useEffect, useState } from "react";



import  { useGoogleLogin } from '@react-oauth/google';
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
        let data = credentialResponse
        let headers= {
            method: "POST",
            mode: "cors",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }
        console.log("FETCHING")

        await fetch('/api/user/authenticate', headers)
        .then(response => response.json())
        .then(data => {
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
            return (<h3>Logged IN to {userData.email}</h3>)
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
            <h3>HELLO</h3>
        </div>
        )
    }

    return(
        <DisplayLoginButton/>
    )
}