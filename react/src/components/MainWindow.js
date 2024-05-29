import React, { useEffect, useState } from "react";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";
import { useNavigate, useParams, useLocation } from 'react-router';
import { createSnapshotForDocument } from "../api/APIUtils";
import { EXTENSION_TO_LANGUAGE_MAP } from "../utils/programLanguageMapping";
import { Button } from "flowbite-react";
import { Tooltip } from "react-tooltip";
import 'react-tooltip/dist/react-tooltip.css'
import BackButton from "./BackButton";


export default function MainWindow( props ) {

  const [comments, setComments] =  useState([])
  const [snapshots, setSnapshots] = useState([])
  const [hasUpdatedCode, setHasUpdatedCode] = useState(false)
  const [editorLanguage, setEditorLanguage] = useState("")


  const [dataToUpload, setDataToUpload] = useState(null) // Null until set to a string value

  const [editorReady, setEditorReady] = useState(false)

  const {project_id, commit_id, document_id, left_snapshot_id} = useParams();

  const location = useLocation();
  const navigate = useNavigate();
  // Handle Setting Program Language that document uses
  useEffect(() => {
    if(!location.state.documentName)
      return
    
    let extensionName = location.state.documentName.split('.')[1].toLowerCase()
    extensionName = EXTENSION_TO_LANGUAGE_MAP[extensionName]

    setEditorLanguage(extensionName)
  }, [location.state.documentName ])


  const handleCreateSnapshotClick = async () => {
    if (!dataToUpload) {
      console.log("No Data To Upload")
      return
    }
    let response = await createSnapshotForDocument(project_id, commit_id, document_id, dataToUpload)

    if (response === null)
      return

    console.log(response);

    navigate(`/Project/${project_id}/Commit/${commit_id}/Document/${document_id}/${left_snapshot_id}/${response}`,
      {state: {documentName: location.state.documentName, addSnapshots: location.state.addSnapshots}})
    
  }

  function DisplaySnapshotCreateButton () {
    if (location.state.addSnapshots !== null) {
      return(
        <div className="text-alternative">
          <Button disabled className="rounded-lg border-2 m-1 opacity-50" data-tooltip-id="addsnapshotbutton">
            Add New Snapshot
          </Button>
          <Tooltip 
            className="z-9999" 
            id="addsnapshotbutton"
            place="bottom"
            disableStyleInjection="true"
            content={
              <div>
                <p>
                  To create a new snapshot, create a working commit
                </p>
                <p>
                  and select a document within the working commit.
                </p>
              </div>
            }
          />
        </div>
      )
    }

    if (hasUpdatedCode === false) {
      return(
        <div className="text-alternative">
          <Button disabled className="rounded-lg border-2 m-1 opacity-50" data-tooltip-id="addsnapshotbutton">
            Add New Snapshot
          </Button>
          <Tooltip 
            className="z-9999" 
            id="addsnapshotbutton"
            place="bottom"
            disableStyleInjection="true"
            content={
              <div>
                <p>
                  To create a new snapshot, modify the code in
                </p>
                <p>
                  the right side of the diff editor.
                </p>
              </div>
            }
          />
        </div>
      )
    }

  return(
    <div className="text-textcolor">
      <Button className="rounded-lg border-2 transition-all duration-300
      hover:bg-alternative m-1" data-tooltip-id="addsnapshotbutton" onClick={handleCreateSnapshotClick}>
        Add New Snapshot
      </Button>
      <Tooltip 
        className="z-9999" 
        id="addsnapshotbutton"
        place="bottom"
        disableStyleInjection="true"
        content={
          <div>
            <p>
              This will create a new snapshot. The most recently
            </p>
            <p>
              created snapshot will be added to your working commit.
            </p>
          </div>
        }
      />
    </div>
  )
}

  if (props.isLoggedIn) {
    return(
      <section>
        <div>
          <BackButton location={`/Project/${project_id}/Commit/${commit_id}`}/>
        </div>
        <div className="">
          <div className="flex">
            <SnapshotSelector
              comments={comments}
              snapshots={snapshots}
              setSnapshots={setSnapshots}
              fileExtensionName={location.state.documentName}
              canAddSnapshots={location.state.addSnapshots}
              editorReady={editorReady}
            />
            <DisplaySnapshotCreateButton/>
          </div>

          <ReviewWindow
            comments={comments}
            setComments={setComments}
            userData={props.userData}
            latestSnapshotData={snapshots[snapshots.length - 1]}
            editorReady={editorReady}
            setEditorReady={setEditorReady}
            setHasUpdatedCode={setHasUpdatedCode}
            setDataToUpload={setDataToUpload}
            editorLanguage={editorLanguage}
            />
        </div>
      </section>

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