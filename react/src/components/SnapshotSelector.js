import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import { truncateString, getColor } from "../utils/utils";
import { Dropdown } from "flowbite-react";
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css'

/**
 * Component for a snapshot selector for the review window to select file version
 *
 * @component
    <SnapshotSelector
      comments={comments}
      snapshots={snapshots}
      setSnapshots={setSnapshots}
      fileExtensionName={location.state.documentName}
      canAddSnapshots={location.state.addSnapshots}
      editorReady={editorReady}
    />
 * 
 * @example
    <MainWindow isLoggedIn={isLoggedIn} userData={userData}/>
 *
 * @param {object} props - Component props
 * @param {Array} props.comments - Array of all comments for project to display
 * @param {Array} props.snapshots - Array of snapshot objects
 * @param {Function} props.setSnapshots - Function to set the snapshots variable
 * @param {string} props.fileExtensionName - String that is used to call navigate with location so that they have fileExtension name
 * @param {boolean} props.canAddSnapshots - Boolean determining if a snapshot can be added
 * @param {boolean} props.editorReady - Boolean determining if the editor is ready or not, any changes will cause reloading snapshots for document
 * 
 */

export default function SnapshotSelector( props ) { 
    const [selectedLeftSnapshotIndex, setSelectedLeftSnapshotIndex] = useState(0)
    const [selectedRightSnapshotIndex, setSelectedRightSnapshotIndex] = useState(0)

    const navigate = useNavigate()

    const {project_id, commit_id, document_id, left_snapshot_id, right_snapshot_id} = useParams()
    
    // Get snapshots for document
    useEffect(() => {
        const grabSnapshots = async () => {
          let result = await getAllSnapshotsFromDocument(project_id, document_id)
          
          if (result === undefined)
            return

          if (result.success)
            props.setSnapshots(result.body.reverse())
        }

        if (props.snapshots.length === 0 || !props.snapshots.some(snapshot => snapshot.snapshot.snapshot_id === Number(right_snapshot_id)))
          grabSnapshots()
        
    }, [document_id, props.editorReady, project_id, props.setSnapshots, props.snapshots, right_snapshot_id])
    
    // Set Snapshot Selecter Snapshot Number
    useEffect(() => {
      if(props.snapshots.length === 0 || (props.snapshots[selectedLeftSnapshotIndex].snapshot.snapshot_id === left_snapshot_id &&
        props.snapshots[selectedRightSnapshotIndex].snapshot.snapshot_id === right_snapshot_id
        ) )
        return
      
      props.snapshots.forEach((snapshot, index) => {
        const currentSnapshot_id = snapshot.snapshot.snapshot_id.toString()
        if(currentSnapshot_id === left_snapshot_id)
          setSelectedLeftSnapshotIndex(index)
        if(currentSnapshot_id === right_snapshot_id)
          setSelectedRightSnapshotIndex(index)
      });
    }, [props.snapshots, left_snapshot_id, right_snapshot_id, selectedLeftSnapshotIndex, selectedRightSnapshotIndex])

    async function handleLeftSnapClick(selectedSnapshot, selectedIndex) {
      setSelectedLeftSnapshotIndex(selectedIndex)
      navigate(`/Project/${project_id}/Commit/${commit_id}/Document/${document_id}/${selectedSnapshot}/${right_snapshot_id}`,
        {state: {documentName: props.fileExtensionName, addSnapshots: props.canAddSnapshots}})
    }

    async function handleRightSnapClick(selectedSnapshot, selectedIndex) {
      setSelectedRightSnapshotIndex(selectedIndex)
      navigate(`/Project/${project_id}/Commit/${commit_id}/Document/${document_id}/${left_snapshot_id}/${selectedSnapshot}`,
        {state: {documentName: props.fileExtensionName, addSnapshots: props.canAddSnapshots}})
    }

    function filterComments(snapshot) {
      if (props.comments.length > 0)
        return props.comments.filter(comment => (comment.snapshot_id === snapshot.snapshot.snapshot_id) && (comment.is_resolved === false)).length
      
      return 0
    }

    function DisplayLeftSnapshots() {
        if(props.snapshots.length !== 0) {
            return (
              <Dropdown 
                className= "z-9999 bg-background" label={
                  <div className="flex max-w-sm">
                    <div className="flex-1 flex-grow w-full flex-col text-textcolor whitespace-nowrap">
                      {`${truncateString(props.snapshots[selectedLeftSnapshotIndex].commit.name, 50)}`}
                    </div>
                  </div>
                }>
                {props.snapshots.map((snapshot, index) => { 
                    const value = filterComments(snapshot)
                    let str = ""
                    if (value !== 0)
                      str = `(${value})`
                    //console.log(snapshot)
                    return (
                      <Dropdown.Item 
                        className="z-9999 bg-background hover:bg-alternative"
                        key={index}
                        onClick={() => handleLeftSnapClick(snapshot.snapshot.snapshot_id, index)}
                        data-tooltip-id={`tooltipleft${index}`}
                      >
                        <div className="flex">
                          <div className="flex-1 flex-grow flex-col text-textcolor whitespace-nowrap mr-2">
                            {`${truncateString(snapshot.commit.name, 40)}`}
                          </div>
                          <div className={"flex-1 " + getColor(snapshot.commit.state)}>
                            {`*${snapshot.commit.state.toString().toUpperCase()}`}
                          </div>
                          <div className="ml-3">
                            {str}
                          </div>
                        </div>
                        <Tooltip
                          className="z-9999" 
                          id={`tooltipleft${index}`}
                          place="right"
                          content={
                            <div>
                              <p>
                                Last Modified: {new Date(snapshot.snapshot.date_modified).toLocaleString()}
                              </p>
                              <p>
                                Open Comments: {value}
                              </p>
                            </div>
                          }
                        />
                      </Dropdown.Item>
                    )
                })}
              </Dropdown>
            )
         } 
         else {
            return <div>EMPTY</div>
         }
    }
    
    function DisplayRightSnapshots() {
      if(props.snapshots.length !== 0) {
          return (
            <Dropdown className="z-9999 bg-background" label={
              <div className="flex max-w-sm">
                <div className="flex-1 flex-grow w-full flex-col text-textcolor whitespace-nowrap">
                  {`${truncateString(props.snapshots[selectedRightSnapshotIndex].commit.name, 50)}`}
                </div>
              </div>
            }>
              {props.snapshots.map((snapshot, index) => { 
                  const value = filterComments(snapshot)
                  let str = ""
                  if (value !== 0)
                    str = `(${value})`
                  //console.log(snapshot.snapshot_id, right_snapshot_id, snapshot.snapshot_id === right_snapshot_id )
                  return (
                    <Dropdown.Item 
                      className="z-9999 bg-background hover:bg-alternative"
                      key={index}
                      onClick={() => handleRightSnapClick(snapshot.snapshot.snapshot_id, index)}
                      data-tooltip-id={`tooltipright${index}`}
                    >
                      <div className="flex">
                        <div className="flex-1 flex-grow flex-col text-textcolor whitespace-nowrap mr-2">
                          {`${truncateString(snapshot.commit.name, 40)}`}
                        </div>
                        <div className={"flex-1 " + getColor(snapshot.commit.state)}>
                          {`*${snapshot.commit.state.toString().toUpperCase()}`}
                        </div>
                        <div className="ml-3">
                          {str}
                        </div>
                      </div>
                      <Tooltip
                        className="z-9999" 
                        id={`tooltipright${index}`}
                        place="right"
                        content={
                          <div>
                            <p>
                              Last Modified: {new Date(snapshot.snapshot.date_modified).toLocaleString()}
                            </p>
                            <p>
                              Open Comments: {value}
                            </p>
                          </div>
                        }
                      />
                    </Dropdown.Item>
                  )
              })}           
            </Dropdown>
          )
       } 
       else {
          return <div>EMPTY</div>
       }
  }

    return (
        <div className="w-2/3 text-textcolor flex">
          <div className="w-1/2 m-1">
            <DisplayLeftSnapshots/>
          </div>
          <div className="w-1/2 m-1">
            <DisplayRightSnapshots/>
          </div>
        </div>
    )
}