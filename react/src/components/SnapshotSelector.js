import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css'
import './SnapshotSelector.css'

export default function SnapshotSelector() { 
    const [snapshots, setSnapshots] = useState([])
    const [selectedLeftSnapshotIndex, setSelectedLeftSnapshotIndex] = useState(0)
    const [selectedRightSnapshotIndex, setSelectedRightSnapshotIndex] = useState(0)

    const navigate = useNavigate()

    const {document_id, left_snapshot_id, right_snapshot_id} = useParams()
    // Get snapshots for document
    useEffect(() => {

        const grabSnapshots = async () => {
          let result = await getAllSnapshotsFromDocument(document_id)
          console.log(result)
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

    function DisplayLeftSnapshots() {
        if(snapshots.length !== 0) {
            return (
              <div>
                <div>Dsiplay on Left</div>
                {snapshots.map((snapshot, index) => { 
                    //console.log(snapshot)
                    return (index <= selectedRightSnapshotIndex) ? (
                      <div key={index}>
                        <button 
                          id={snapshot.snapshot_id.toString() === left_snapshot_id ? 'Selected-Item' : null}
                          onClick={() => handleLeftSnapClick(snapshot.snapshot_id, index)}
                          data-tooltip-id={`tooltipleft${index}`}>
                            Snapshot {index}
                        </button>
                        <Tooltip 
                          id={`tooltipleft${index}`}
                          place="bottom"
                          content={`Last Modified: ${new Date(snapshot.date_modified).toLocaleString()}`}
                        />
                      </div>
                    ) : null
                })}              
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
              {snapshots.map((snapshot, index) => { 
                  //console.log(snapshot.snapshot_id, right_snapshot_id, snapshot.snapshot_id === right_snapshot_id )
                  
                  return (index >= selectedLeftSnapshotIndex) ? (
                    <div key={index}>
                      <button 
                        id={snapshot.snapshot_id.toString() === right_snapshot_id ? 'Selected-Item' : null}
                        onClick={() => handleRightSnapClick(snapshot.snapshot_id, index)}
                        data-tooltip-id={`tooltipright${index}`}>
                          Snapshot {index}
                      </button>
                      <Tooltip 
                        id={`tooltipright${index}`}
                        place="bottom"
                        content={`Last Modified: ${new Date(snapshot.date_modified).toLocaleString()}`}
                      />
                    </div>
                  ) : null
              })}              
            </div>
        )
       } 
       else {
          return <div>EMPTY</div>
       }
  }

    return (
        <div className="Snapshot-selector">
            <div>
              <DisplayLeftSnapshots/>
              <DisplayRightSnapshots/>              
            </div>

        </div>
    )
}