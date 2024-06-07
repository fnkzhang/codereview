import React, { useEffect, useCallback } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from 'jwt-decode';
import { Dropdown, Avatar } from 'flowbite-react';
import getCookie, { deleteCookie } from "../utils/utils";
import GitHubStatus from "./GitHub/GitHubStatus";



/**
 * Google OAuth component to handle user login
 *
 * @component
 * 
 * @example
    <Oauth
      isLoggedIn={isLoggedIn}
      setIsLoggedIn={setIsLoggedIn}
      userData={userData}
      setUserData={setUserData}
      connected={connected}
      setConnected={setConnected}
    />
 *
 * @param {object} props - Component props
 * @param {boolean} props.isLoggedIn - Boolean to determine if use is logged in or not
 * @param {Function} props.setIsLoggedIn - State function to set isLoggedIn
 * @param {object} props.useData - Object holding Google OAuth user data
 * @param {Function} props.setUserData - State function to set setUserData
 * @param {boolean} props.connected - Boolean determining if OAuth is connected
 * @param {Function} props.setConnected - State function to set connected
 * 
 */
export default function Oauth( props ){

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
            
            props.setUserData(data.body)
            props.setIsLoggedIn(true)
            // Save to Cookie
            document.cookie = `cr_id_token=${credentialResponse.credential}; domain=; path=/`;
        })
        .catch(e => console.log(e))
    }, [props])

    // Check If the user token is valid
    useEffect(() => {
        if (props.isLoggedIn === false) {
            let credentialToken = getCookie("cr_id_token")
            if (credentialToken === null) {
              props.setIsLoggedIn(false)
                props.setUserData(null)
                return
            }

            let credentialObject = {
                "credential": credentialToken
            }
            verifyLogin(credentialObject)
        }


    }, [props, verifyLogin])

    // Check if user is valid when userData is returned
    useEffect(() => {
        if(props.userData === null)
            return

        const x = async () => {
            // Signup user if they are not in database
            let result = await checkIfUserExists(props.userData["email"])

            if(!result) {
                console.log("Signing up user because they do not exist in database")
                signupUser(props.userData["email"])            
            }
        }
        x()

    }, [props.userData])

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
    
    async function signupUser(email) {
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
            console.log("SIGNED UP USER")
            console.log(data)
        })
        .catch(e => console.log(e))

    }

    function displayProfileImage() {
        return (<Avatar
          img={props.userData.picture}
          alt="?"
          className='w-10 h-10 rounded-sm ml-2'/>
        )
    }

    function handleLogout() {
        deleteCookie("cr_id_token")
        props.setConnected(false)
        props.setIsLoggedIn(false)
    }
    

    if (props.isLoggedIn) {
      return (
        <div className="flex">
        <Dropdown
          inline
          className="bg-background"
          label="Account"
        >
          <Dropdown.Item className="bg-background" onClick={handleLogout}>Logout</Dropdown.Item>
          <Dropdown.Item className="bg-background">
            <GitHubStatus
              connected={props.connected}
              setConnected={props.setConnected}
            />
          </Dropdown.Item>
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
