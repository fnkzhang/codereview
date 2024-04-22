import React, { useEffect, useCallback } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from 'jwt-decode';
import { Dropdown, Avatar } from 'flowbite-react';
import getCookie, { deleteCookie } from "../utils/utils";

export default function Oauth( { isLoggedIn, setIsLoggedIn, userData, setUserData } ){

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
            console.log(userData)
            setIsLoggedIn(true)
            // Save to Cookie
            document.cookie = `cr_id_token=${credentialResponse.credential}; domain=; path=/`;
        })
        .catch(e => console.log(e))
    }, [setIsLoggedIn, setUserData])

    // Check If the user token is valid
    useEffect(() => {
        if (isLoggedIn === false) {
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
        }


    }, [verifyLogin, isLoggedIn, setIsLoggedIn, setUserData])

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

    function displayProfileImage() {
        return (<Avatar
          img={userData.picture}
          alt="?"
          className='w-10 h-10 rounded-sm ml-2'/>
        )
    }

    function handleLogout() {
        deleteCookie("cr_id_token")
        setIsLoggedIn(false)
    }
    

    if (isLoggedIn) {
      return (
        <div className="flex">
        <Dropdown
          inline
          className="bg-background"
          label="Account"
        >
          <Dropdown.Item className="bg-background" onClick={handleLogout}>Logout</Dropdown.Item>
          <Dropdown.Item className="bg-background">Connect to Github</Dropdown.Item>
        </Dropdown>
        {displayProfileImage()}
        </div>
      )
    }

    return (
      <div>
        <GoogleLogin 
            className="bg-background m-1 inline-block p-5"
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
