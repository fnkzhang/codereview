import React, { useEffect, useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";
import { useNavigate, useParams } from 'react-router';
import { createSnapshotForDocument } from "../api/APIUtils";

export default function MainWindow( props ) {

  const [comments, setComments] =  useState([])
  const [snapshots, setSnapshots] = useState([])
  const [hasUpdatedCode, setHasUpdatedCode] = useState(false)
  
  const [dataToUpload, setDataToUpload] = useState(null) // Null until set to a string value

  const {project_id, document_id, left_snapshot_id, right_snapshot_id} = useParams()

  const navigate = useNavigate()
  const handleCreateSnapshotClick = async () => {
    if (!dataToUpload) {
      console.log("No Data To Upload")
      return
    }

    
    let response = await createSnapshotForDocument(project_id, document_id, dataToUpload)
    if (response === null)
      return
      
    navigate(`/Project/${project_id}/Document/${document_id}/${left_snapshot_id}/${response}`)
    
  }

  const DisplaySnapshotCreateButton = () => {



    return (
    <div className=" m-5 text-textcolor text-xl ">
      <button className="p-3 rounded-lg border-2 transition-all duration-300
       hover:bg-alternative m-1" onClick={handleCreateSnapshotClick}>
        Add New Snapshot
      </button> 
    </div>
      
  )}

  useEffect(() => {
    console.log(hasUpdatedCode, "SWTG")
  }, [hasUpdatedCode])

  if (props.isLoggedIn) {
    // console.log(snapshots)
    // console.log(hasUpdatedCode)
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
          setHasUpdatedCode={setHasUpdatedCode}
          setDataToUpload={setDataToUpload}/>
          
         
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