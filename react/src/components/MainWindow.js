import React, { useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";
import Oauth from "./Oauth"
import AppHeader from "./AppHeader"
import "./MainWindow.css"

export default function MainWindow() {

  const [isLoggedIn, setIsLoggedIn] = useState(false)
  
  if (isLoggedIn) {
    return(
      <div>
        <Oauth
          isLoggedIn={isLoggedIn}
          setIsLoggedIn={setIsLoggedIn}/>
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
          setIsLoggedIn={setIsLoggedIn}/>
        <AppHeader/>
        <div className="Logged-out-message">
          You must Log in to view this page.
        </div>
      </div>
    )
  }
}