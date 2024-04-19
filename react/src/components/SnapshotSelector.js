import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import { Dropdown } from "flowbite-react";
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css'

export default function SnapshotSelector({ comments }) { 
    const [selectedLeftSnapshotIndex, setSelectedLeftSnapshotIndex] = useState(0)
    const [selectedRightSnapshotIndex, setSelectedRightSnapshotIndex] = useState(0)

    const [snapshots, setSnapshots] = useState([])
    const navigate = useNavigate()

    const {project_id, document_id, left_snapshot_id, right_snapshot_id} = useParams()
    // Get snapshots for document
    useEffect(() => {

        const grabSnapshots = async () => {
          let result = await getAllSnapshotsFromDocument(document_id)
          //console.log(result)
          if (result.success)
            setSnapshots(result.body)
        }

        grabSnapshots()
    }, [document_id])

    async function handleLeftSnapClick(selectedSnapshot, selectedIndex) {
      setSelectedLeftSnapshotIndex(selectedIndex)
      navigate(`/Project/${project_id}/Document/${document_id}/${selectedSnapshot}/${right_snapshot_id}`)
    }

    async function handleRightSnapClick(selectedSnapshot, selectedIndex) {
      setSelectedRightSnapshotIndex(selectedIndex)
      navigate(`/Project/${project_id}/Document/${document_id}/${left_snapshot_id}/${selectedSnapshot}`)
    }

    function filterComments(snapshot) {
      if (comments.length > 0)
        return comments.filter(comment => (comment.snapshot_id === snapshot.snapshot_id) && (comment.is_resolved === false)).length
      
      return []
    }

    function DisplayLeftSnapshots() {
        if(snapshots.length !== 0) {
            return (
              <Dropdown 
                className= "z-9999 bg-background" label={`Snapshot ${selectedLeftSnapshotIndex}`}>
                {snapshots.map((snapshot, index) => { 
                    const value = filterComments(snapshot)
                    let str = ""
                    if (value !== 0)
                      str = `(${value})`
                    //console.log(snapshot)
                    return (index <= selectedRightSnapshotIndex) ? (
                      <Dropdown.Item 
                        className="z-9999 bg-background"
                        key={index}
                        onClick={() => handleLeftSnapClick(snapshot.snapshot_id, index)}
                        data-tooltip-id={`tooltipleft${index}`}
                      >
                        Snapshot {index} {str}
                        <Tooltip
                          className="z-9999" 
                          id={`tooltipleft${index}`}
                          place="right"
                          content={
                            <div>
                              <p>
                                Last Modified: {new Date(snapshot.date_modified).toLocaleString()}
                              </p>
                              <p>
                                Open Comments: {value}
                              </p>
                            </div>
                          }
                        />
                      </Dropdown.Item>
                    ) : null
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
            <Dropdown className="z-9999 bg-background" label={`Snapshot ${selectedRightSnapshotIndex}`}>
              {snapshots.map((snapshot, index) => { 
                  const value = filterComments(snapshot)
                  let str = ""
                  if (value !== 0)
                    str = `(${value})`
                  //console.log(snapshot.snapshot_id, right_snapshot_id, snapshot.snapshot_id === right_snapshot_id )
                  return (index >= selectedLeftSnapshotIndex) ? (
                    <Dropdown.Item 
                      className="z-9999 bg-background"
                      key={index}
                      onClick={() => handleRightSnapClick(snapshot.snapshot_id, index)}
                      data-tooltip-id={`tooltipright${index}`}
                    >
                      Snapshot {index} {str}
                      <Tooltip
                        className="z-9999" 
                        id={`tooltipright${index}`}
                        place="right"
                        content={
                          <div>
                            <p>
                              Last Modified: {new Date(snapshot.date_modified).toLocaleString()}
                            </p>
                            <p>
                              Open Comments: {value}
                            </p>
                          </div>
                        }
                      />
                    </Dropdown.Item>
                  ) : null
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