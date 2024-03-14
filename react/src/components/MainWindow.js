import React, { useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";
import Oauth from "./Oauth"
import AppHeader from "./AppHeader"
import "./MainWindow.css"

export default function MainWindow() {

  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userData, setUserData] = useState(null)
  
  if (isLoggedIn) {
    return(
      <div>
        <Oauth
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        userData={userData}
        setUserData={setUserData}/>
        <AppHeader/>
        <SnapshotSelector/>
        <ReviewWindow/>
      </div>
    )
  } else {
    return(
      <div>
        <Oauth
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        userData={userData}
        setUserData={setUserData}/>
        <AppHeader/>
        <div className="Logged-out-message">
          You must Log in to view this page.
        </div>
      </div>
    )
  }
}