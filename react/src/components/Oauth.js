import "./Oauth.css"
import React, { useEffect, useState, useCallback } from "react";
import { GoogleLogin } from "@react-oauth/google";

import { jwtDecode } from 'jwt-decode';
import getCookie from "../utils/utils";

export default function Oauth( { isLoggedIn, setIsLoggedIn } ){

    const [userData, setUserData] = useState(null)

    const verifyLogin = useCallback(async (credentialResponse) => {
        let oAuthToken = credentialResponse.credential
        
        let headers= {
            method: "POST",
            mode: "cors",
            headers: {
              "Authorization": oAuthToken,
              "Content-Type": "application/json"
            },
        }

        await fetch('/api/user/authenticate', headers)
        .then(response => response.json())
        .then(data => {
            if (data.success === false) {
                console.log("Failed to validate token")
                return
            }
            
            setUserData(data.body)
            console.log("Valid Token Provided, Saving to cookies")
            setIsLoggedIn(true)
            // Save to Cookie
            document.cookie = `cr_id_token=${credentialResponse.credential}; domain=; path=/`;
        })
        .catch(e => console.log(e))
    }, [setIsLoggedIn])

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

    }, [verifyLogin, setIsLoggedIn])

    // Check if user is valid when userData is returned
    useEffect(() => {
        if(userData === null)
            return

        const x = async () => {
            // Singup user if they are not in database
            let result = await checkIfUserExists(userData["email"])

            if(!result) {
                console.log("Signing up user because they do not exist in database")
                singupUser(userData["email"])            
            }
        }
        x()

    }, [userData])

    async function checkIfUserExists(email) {
        let credential = getCookie("cr_id_token")

        let headers= {
            method: "POST",
            mode: "cors",
            headers: {
              "Authorization": credential,
              "Email": email,
              "Content-Type": "application/json"
            }
        }

        return await fetch('/api/user/isValidUser', headers)
        .then(response => response.json())
        .then(data => data.success)
        .catch(e => console.log(e))
    }
    
    async function singupUser(email) {
        let credential = getCookie("cr_id_token")

        let headers= {
            method: "POST",
            mode: "cors",
            headers: {
              "Authorization": credential,
              "Email": email,
              "Content-Type": "application/json"
            }
        }

        await fetch('/api/user/signup', headers)
        .then(response => response.json())
        .then(data => {
            console.log("SINGED UP USER")
            console.log(data)
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
