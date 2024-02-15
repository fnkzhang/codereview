import React from "react";



import  { useGoogleLogin } from '@react-oauth/google';
import { GoogleLogin } from "@react-oauth/google";

import { jwtDecode } from 'jwt-decode';

export default function Oauth(){

    const login = useGoogleLogin({
        onSuccess: async tokenResponse => {
            console.log(tokenResponse)
            let headers= {
                method: "POST",
                mode: "cors",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify(tokenResponse)
            }
            await fetch('/api/user/authenticate', headers)
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(e => console.log(e))

        },
        //flow: 'auth-code',
    })

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
        .then(data => console.log(data))
        .catch(e => console.log(e))
    }

    return(
        <div>
            <button onClick={() => login()}>Login With Google</button>
            <GoogleLogin
                onSuccess={credentialResponse => {
                let decodedResponse = jwtDecode(credentialResponse.credential)
                console.log(decodedResponse)
                console.log(credentialResponse)
                credentialResponse["credential"] = credentialResponse["credential"] + "fjarg"
                
                console.log(credentialResponse)
                verifyLogin(credentialResponse)
                }}
                onError={() => {console.log("Failed To login")}}
            />
            <h3>HELLO</h3>
        </div>
    )
}