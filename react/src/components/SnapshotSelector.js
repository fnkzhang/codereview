import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css'

export default function SnapshotSelector({ comments }) { 
    const [selectedLeftSnapshotIndex, setSelectedLeftSnapshotIndex] = useState(0)
    const [selectedRightSnapshotIndex, setSelectedRightSnapshotIndex] = useState(0)

    const [snapshots, setSnapshots] = useState([])
    const navigate = useNavigate()

    const {document_id, left_snapshot_id, right_snapshot_id} = useParams()
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
      navigate(`/Document/${document_id}/${selectedSnapshot}/${right_snapshot_id}`)
    }

    async function handleRightSnapClick(selectedSnapshot, selectedIndex) {
      setSelectedRightSnapshotIndex(selectedIndex)
      navigate(`/Document/${document_id}/${left_snapshot_id}/${selectedSnapshot}`)
    }

    function filterComments(snapshot) {
      if (comments.length > 0)
        return comments.filter(comment => (comment.snapshot_id === snapshot.snapshot_id) && (comment.is_resolved === false)).length
      
      return []
    }

    function DisplayLeftSnapshots() {
        if(snapshots.length !== 0) {
            return (
              <div>
                <div>Dsiplay on Left</div>
                <div style={{"display": "flex"}}>
                  {snapshots.map((snapshot, index) => { 
                      const value = filterComments(snapshot)
                      let str = ""
                      if (value !== 0)
                        str = `(${value})`
                      //console.log(snapshot)
                      return (index <= selectedRightSnapshotIndex) ? (
                        <div key={index}>
                          <button 
                            className={snapshot.snapshot_id.toString() === left_snapshot_id ? 'bg-snapshotSelected' : null}
                            onClick={() => handleLeftSnapClick(snapshot.snapshot_id, index)}
                            data-tooltip-id={`tooltipleft${index}`}>
                              Snapshot {index} {str}
                          </button>
                          <Tooltip
                            className="z-9999" 
                            id={`tooltipleft${index}`}
                            place="bottom"
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
                        </div>
                      ) : null
                  })} 
                </div> 
              </div>
          )
         } 
         else {
            return <div>EMPTY</div>
         }
    }
    
    function DisplayRightSnapshots() {
      if(snapshots.length !== 0) {
          return (
            <div>
              <div>Dsiplay on Right</div>
              <div style={{"display": "flex"}}>
                {snapshots.map((snapshot, index) => { 
                    const value = filterComments(snapshot)
                    let str = ""
                    if (value !== 0)
                      str = `(${value})`
                    //console.log(snapshot.snapshot_id, right_snapshot_id, snapshot.snapshot_id === right_snapshot_id )
                    return (index >= selectedLeftSnapshotIndex) ? (
                      <div key={index}>
                        <button 
                          className={snapshot.snapshot_id.toString() === right_snapshot_id ? 'bg-snapshotSelected' : null}
                          onClick={() => handleRightSnapClick(snapshot.snapshot_id, index)}
                          data-tooltip-id={`tooltipright${index}`}>
                            Snapshot {index} {str}
                        </button>
                        <Tooltip
                          className="z-9999" 
                          id={`tooltipright${index}`}
                          place="bottom"
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
                      </div>
                    ) : null
                })} 
              </div>             
            </div>
        )
       } 
       else {
          return <div>EMPTY</div>
       }
  }

    return (
        <div className="text-textcolor">
            <div>
              <DisplayLeftSnapshots/>
              <DisplayRightSnapshots/>              
            </div>

        </div>
    )
}