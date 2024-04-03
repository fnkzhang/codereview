import React, { useEffect, useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";
import Oauth from "./Oauth"
import AppHeader from "./AppHeader"
import "./Logged-out.css"

import { getComments } from '../dev/getComments.js'

export default function MainWindow() {

  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userData, setUserData] = useState(null)
  const [comments, setComments] =  useState([])

  const [snapshots, setSnapshots] = useState([])

  if (isLoggedIn) {
    console.log(snapshots)
    return(
      <div>
        <Oauth
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        userData={userData}
        setUserData={setUserData}/>
        <AppHeader/>
        <SnapshotSelector
          comments={comments}
          snapshots={snapshots}
          setSnapshots={setSnapshots}/>
        <ReviewWindow
          comments={comments}
          setComments={setComments}
          userData={userData}
          snapshots={snapshots}/>
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