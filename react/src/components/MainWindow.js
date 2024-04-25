import React, { useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";

export default function MainWindow( props ) {

  const [comments, setComments] =  useState([])
  const [snapshots, setSnapshots] = useState([])

  if (props.isLoggedIn) {
    console.log(snapshots)
    return(
      <div className="h-screen">
        <SnapshotSelector
          comments={comments}
          snapshots={snapshots}
          setSnapshots={setSnapshots}/>
        <ReviewWindow
          comments={comments}
          setComments={setComments}
          userData={props.userData}
          snapshots={snapshots}/>
      </div>
    )
  }
  
  return(
    <div>
      <div className="m-20 text-center text-textcolor text-2xl">
        You must Log in to view this page.
      </div>
    </div>
  )
}