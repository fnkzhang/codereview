import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import { Dropdown } from "flowbite-react";
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css'

export default function SnapshotSelector({ comments, snapshots, setSnapshots, fileExtensionName, canAddSnapshots, editorReady }) { 
    const [selectedLeftSnapshotIndex, setSelectedLeftSnapshotIndex] = useState(0)
    const [selectedRightSnapshotIndex, setSelectedRightSnapshotIndex] = useState(0)

    const navigate = useNavigate()

    const {project_id, commit_id, document_id, left_snapshot_id, right_snapshot_id} = useParams()
    
    // Get snapshots for document
    useEffect(() => {
        const grabSnapshots = async () => {
          let result = await getAllSnapshotsFromDocument(project_id, document_id)
          console.log(result)
          if (result.success)
            setSnapshots(result.body)
        }

        if (snapshots.length === 0 )
          grabSnapshots()
        
    }, [document_id, editorReady, project_id, setSnapshots, snapshots])
    
    // Set Snapshot Selecter Snapshot Number
    useEffect(() => {
      if(snapshots.length === 0 || (snapshots[selectedLeftSnapshotIndex].snapshot.snapshot_id === left_snapshot_id &&
        snapshots[selectedRightSnapshotIndex].snapshot.snapshot_id === right_snapshot_id
        ) )
        return
      
      snapshots.forEach((snapshot, index) => {
        const currentSnapshot_id = snapshot.snapshot.snapshot_id.toString()
        if(currentSnapshot_id === left_snapshot_id)
          setSelectedLeftSnapshotIndex(index)
        if(currentSnapshot_id === right_snapshot_id)
          setSelectedRightSnapshotIndex(index)
      });
    }, [snapshots, left_snapshot_id, right_snapshot_id, selectedLeftSnapshotIndex, selectedRightSnapshotIndex])

    async function handleLeftSnapClick(selectedSnapshot, selectedIndex) {
      setSelectedLeftSnapshotIndex(selectedIndex)
      navigate(`/Project/${project_id}/Commit/${commit_id}/Document/${document_id}/${selectedSnapshot}/${right_snapshot_id}`,
        {state: {documentName: fileExtensionName, addSnapshots: canAddSnapshots}})
    }

    async function handleRightSnapClick(selectedSnapshot, selectedIndex) {
      setSelectedRightSnapshotIndex(selectedIndex)
      navigate(`/Project/${project_id}/Commit/${commit_id}/Document/${document_id}/${left_snapshot_id}/${selectedSnapshot}`,
        {state: {documentName: fileExtensionName, addSnapshots: canAddSnapshots}})
    }

    function filterComments(snapshot) {
      if (comments.length > 0)
        return comments.filter(comment => (comment.snapshot_id === snapshot.snapshot.snapshot_id) && (comment.is_resolved === false)).length
      
      return 0
    }

    function DisplayLeftSnapshots() {
        if(snapshots.length !== 0) {
            return (
              <Dropdown 
                className= "z-9999 bg-background" label={`${snapshots[selectedLeftSnapshotIndex].commit.name}`}>
                {snapshots.map((snapshot, index) => { 
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
                        {snapshot.commit.name} {str}
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
      if(snapshots.length !== 0) {
          return (
            <Dropdown className="z-9999 bg-background" label={`${snapshots[selectedRightSnapshotIndex].commit.name}`}>
              {snapshots.map((snapshot, index) => { 
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
                      {snapshot.commit.name} {str}
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