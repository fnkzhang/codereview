import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import './SnapshotSelector.css'

// todo testing remove later
import Oauth from "./Oauth.js";

export default function SnapshotSelector() { 
    const [snapshots, setSnapshots] = useState([])
    const [selectedLeftSnapshotIndex, setSelectedLeftSnapshotIndex] = useState(0)

    const navivate = useNavigate()

    const {document_id, left_snapshot_id, right_snapshot_id} = useParams()
    // Get snapshots for document
    useEffect(() => {
      console.log(document_id, left_snapshot_id, right_snapshot_id)

        const grabSnapshots = async () => {
            let result = await getAllSnapshotsFromDocument(document_id)

            if (result.success)
              setSnapshots(result.body)
        }

        grabSnapshots()
    }, [])

    async function handleLeftSnapClick(selectedSnapshot, selectedIndex) {
      console.log(selectedSnapshot, selectedIndex)
      setSelectedLeftSnapshotIndex(selectedIndex)
      navivate(`/Document/${document_id}/${selectedSnapshot}/${selectedSnapshot}`)
      navivate(0)

    }
    async function handleRightSnapClick(selectedSnapshot, selectedIndex) {
      console.log(selectedSnapshot, selectedIndex)
      navivate(`/Document/${document_id}/${left_snapshot_id}/${selectedSnapshot}`)
      navivate(0)

    }

    function DisplayLeftSnapshots() {
        console.log(snapshots)
        if(snapshots.length !== 0) {
            return (
              <div>
                {snapshots.map((snapshot, index) => { 
                    //console.log(snapshot)
                    return (
                      <button key={index} id={snapshot.snapshot_id.toString() === left_snapshot_id ? 'Selected-Item' : null}
                              onClick={() => handleLeftSnapClick(snapshot.snapshot_id, index)}>
                        Left Snap test
                      </button>)
                })}              
              </div>
          )
         } 
         else {
            return null
         }
    }
    
    function DisplayRightSnapshots() {
      console.log(snapshots)
      if(snapshots.length !== 0) {
          return (
            <div>
              {snapshots.map((snapshot, index) => { 
                  //console.log(snapshot.snapshot_id, right_snapshot_id, snapshot.snapshot_id === right_snapshot_id )
                  
                  return (index >= selectedLeftSnapshotIndex) ? (
                    <button key={index} id={snapshot.snapshot_id.toString() === right_snapshot_id ? 'Selected-Item' : null}
                            onClick={() => handleRightSnapClick(snapshot.snapshot_id, index)}>
                      Righttest
                    </button>
                  ) : null
              })}              
            </div>
        )
       } 
       else {
          return null
       }
  }

    return (
        <div>
            <Oauth/>
            <div>
              <DisplayLeftSnapshots/>
              <DisplayRightSnapshots/>              
            </div>

        </div>
    )
}