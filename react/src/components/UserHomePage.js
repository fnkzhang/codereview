import ProjectList  from "./Projects/ProjectList";
import { useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { addGitHubToken } from "../api/APIUtils";

export default function UserHomePage( props ) {
  const [loading, setLoading] = useState(true)

  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const code = queryParams.get('code');

  useEffect(() => {

    async function sendToken() {
      let result = await addGitHubToken(code)

      console.log(result)
    }

    async function sendData() {
      try {
        await Promise.all([
          sendToken()
        ])
      } catch (error) {
        console.log(error)
      } finally {
        setLoading(false)
      }
    }

    if (code && loading){
      sendData()
    }
  })

  if (code) {

    if (loading) {
      return (
        <div>
          <div className="m-20 text-center text-textcolor text-2xl">
            Verifying connection...
          </div>
        </div>
      )
    }
    
    return (
      <div>
        <div className="m-20 text-center text-textcolor text-2xl">
          You have successfully connected your account to GitHub.
        </div>
      </div>
    )
  }

  if (props.isLoggedIn) {
    return (
      <div>          
        <div className="m-5">
          <ProjectList
            isLoggedIn={props.isLoggedIn}
            userData={props.userData}
          />
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="m-20 text-center text-textcolor text-2xl">
        You must Log in to view this page.
      </div>
    </div>
  )
}