import React, { useEffect, useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";
import { useNavigate, useParams, useLocation } from 'react-router';
import { createSnapshotForDocument } from "../api/APIUtils";
import { EXTENSION_TO_LANGUAGE_MAP } from "../utils/programLanguageMapping";

export default function MainWindow( props ) {

  const [comments, setComments] =  useState([])
  const [snapshots, setSnapshots] = useState([])
  const [hasUpdatedCode, setHasUpdatedCode] = useState(false)
  const [editorLanguage, setEditorLanguage] = useState("")

  const [dataToUpload, setDataToUpload] = useState(null) // Null until set to a string value

  const {project_id, document_id, left_snapshot_id, right_snapshot_id} = useParams();

  const location = useLocation();
  const navigate = useNavigate();

  // Handle Setting Program Language that document uses
  useEffect(() => {
    let extensionName = location.state.documentName.split('.')[1].toLowerCase()
    extensionName = EXTENSION_TO_LANGUAGE_MAP[extensionName]

    setEditorLanguage(extensionName)
  }, [location.state.documentName])

  const handleCreateSnapshotClick = async () => {
    if (!dataToUpload) {
      console.log("No Data To Upload")
      return
    }

    let response = await createSnapshotForDocument(project_id, document_id, dataToUpload)
    console.log(response)
    navigate(0)
  }

  const DisplaySnapshotCreateButton = () => (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300
        hover:bg-alternative m-1" onClick={handleCreateSnapshotClick}>
          Add New Snapshot
        </button> 
      </div>
  )

  if (props.isLoggedIn) {
    return(
      <div className="h-screen">
        <div className="flex">
          <SnapshotSelector
            comments={comments}
            snapshots={snapshots}
            setSnapshots={setSnapshots}
            fileExtensionName={location.state.documentName}/>

          {hasUpdatedCode ? <DisplaySnapshotCreateButton/> : null}
        </div>

        <ReviewWindow
          comments={comments}
          setComments={setComments}
          userData={props.userData}
          latestSnapshotData={snapshots[snapshots.length - 1]}
          setHasUpdatedCode={setHasUpdatedCode}
          setDataToUpload={setDataToUpload}
          editorLanguage={editorLanguage}/>
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