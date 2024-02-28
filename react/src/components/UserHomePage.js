import React, {useState, useEffect} from "react";
import utils from "../utils/utils";
import { useNavigate } from "react-router";

export default function UserHomePage() {
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [userData, setUserData] = useState(null)

    const navigate = useNavigate()

    // Validate User or Send to Login
    useEffect(() => {
      let credentialToken = utils.getCookie("cr_id_token")

      if (credentialToken === null)
        return

      let credentialObject = {
          "credential": credentialToken
      }

      verifyLogin(credentialObject)
      // After Setting userData, use email to grab user related documents from API

    }, [])

    useEffect(() => {
      if (userData === null)  
        return

      // todo GRAB USER DATA FROM API

      
    }, [userData])
    async function verifyLogin(credentialResponse) {
      let oAuthToken = credentialResponse.credential

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

    return (
      <div>

      </div>
    )
}