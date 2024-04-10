import React, {useState} from "react";
import Oauth from "./Oauth";
import ProjectList  from "./Projects/ProjectList";

export default function UserHomePage() {

    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [userData, setUserData] = useState(null)

    if (isLoggedIn) {
      return (
        <div>
          <Oauth
            isLoggedIn={isLoggedIn}
            setIsLoggedIn={setIsLoggedIn}
            userData={userData}
            setUserData={setUserData}
          />
          <ProjectList
            userData={userData}
          />
        </div>
      )
    } else {
      return (
        <div>
            <Oauth
            isLoggedIn={isLoggedIn}
            setIsLoggedIn={setIsLoggedIn}
            userData={userData}
            setUserData={setUserData}/>
            <div className="m-20 text-center text-textcolor text-2xl">
              You must Log in to view this page.
            </div>
        </div>
      )
    }
}