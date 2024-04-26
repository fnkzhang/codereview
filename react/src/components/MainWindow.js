import React, { useEffect, useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";
import { useParams } from 'react-router';

export default function MainWindow( props ) {

  const [comments, setComments] =  useState([])
  const [snapshots, setSnapshots] = useState([])
  const [hasUpdatedCode, setHasUpdatedCode] = useState(false)
  
  const [dataToUpload, setDataToUpload] = useState("")

  const {project_id, document_id, left_snapshot_id, right_snapshot_id} = useParams()

  const handleCreateSnapshotClick = (snapshotContents) => {

  }

  const DisplaySnapshotCreateButton = () => {



    return (
    <div className="justify-center">
      <button className="p-3 text-textcolor hover:bg-alternative">TEST</button> 
    </div>
      
  )}

  useEffect(() => {
    console.log(hasUpdatedCode, "SWTG")
  }, [hasUpdatedCode])

  if (props.isLoggedIn) {
    console.log(snapshots)
    console.log(hasUpdatedCode)
    return(
      <div className="h-screen">
        <div className="flex">
          <SnapshotSelector
            comments={comments}
            snapshots={snapshots}
            setSnapshots={setSnapshots}/>
          {hasUpdatedCode ? <DisplaySnapshotCreateButton/> : null}
        </div>

        <ReviewWindow
          comments={comments}
          setComments={setComments}
          userData={props.userData}
          latestSnapshotData={snapshots[snapshots.length - 1]}
          setHasUpdatedCode={setHasUpdatedCode}/>
          
         
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