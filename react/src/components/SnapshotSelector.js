import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import getCookie from "../utils/utils";
import { getCode, getNewCode } from "../dev/getCode.js"
import './SnapshotSelector.css'

// todo testing remove later
import Oauth from "./Oauth.js";

export default function SnapshotSelector() { 
    const [snapshots, setSnapshots] = useState([])
    const [selectedLeftSnapshotIndex, setSelectedLeftSnapshotIndex] = useState(0)
    const [selectedRightSnapshotIndex, setSelectedRightSnapshotIndex] = useState(0)

    const navigate = useNavigate()

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
      navigate(`/Document/${document_id}/${selectedSnapshot}/${right_snapshot_id}`)
    }

    async function handleRightSnapClick(selectedSnapshot, selectedIndex) {
      console.log(selectedSnapshot, selectedIndex)
      setSelectedRightSnapshotIndex(selectedIndex)
      navigate(`/Document/${document_id}/${left_snapshot_id}/${selectedSnapshot}`)
    }

    async function createProj() {
        let oAuthToken = getCookie("cr_id_token")
  
        let headers = {
          method: "POST",
          mode: "cors",
          headers: {
            "Authorization": oAuthToken,
            "Content-Type": "application/json"
          }
        };
      
        await fetch(`/api/Project/testProject/`, headers)
          .then(response => response.json())
          //.then(data => data.snapshots)
          .catch(e => console.log("ERROR", e))
    }
    async function createSnapshot() {
      let oAuthToken = getCookie("cr_id_token")
        
        let bodyData = {
            name: "Modified Code",
            data: getNewCode()
        }
        let headers = {
          method: "POST",
          mode: "cors",
          headers: {
            "Authorization": oAuthToken,
            "Content-Type": "application/json"
          },
          body: JSON.stringify(bodyData)
          
          
        };

        return await fetch(`/api/Snapshot/684153597/386854791/`, headers)
          .then(response => response.json())
          .then(data => console.log(data))
          .catch(e => console.log("ERROR", e))
        // Create Snapshot for testing
    }
    async function createDocument() {
        let oAuthToken = getCookie("cr_id_token")
        
        let bodyData = {
            name: "TestDocument",
            data: "TESTFILECODE"
        }
        let headers = {
          method: "POST",
          mode: "cors",
          headers: {
            "Authorization": oAuthToken,
            "Content-Type": "application/json"
          },
          body: JSON.stringify(bodyData)
          
        };
      
        return await fetch(`/api/Document/684153597/`, headers)
          .then(response => response.json())
          .then(data => console.log(data))
          .catch(e => console.log("ERROR", e))
    }


    function DisplayLeftSnapshots() {
        console.log(snapshots)
        if(snapshots.length !== 0) {
            return (
              <div>
                <div>Dsiplay on Left</div>
                {snapshots.map((snapshot, index) => { 
                    //console.log(snapshot)
                    return (index <= selectedRightSnapshotIndex) ? (
                      <button id={snapshot.snapshot_id.toString() === left_snapshot_id ? 'Selected-Item' : null}
                              onClick={() => handleLeftSnapClick(snapshot.snapshot_id, index)}>
                        {snapshot.date_modified}
                      </button>
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
      console.log(snapshots)
      if(snapshots.length !== 0) {
          return (
            <div>
              <div>Dsiplay on Right</div>
              {snapshots.map((snapshot, index) => { 
                  //console.log(snapshot.snapshot_id, right_snapshot_id, snapshot.snapshot_id === right_snapshot_id )
                  
                  return (index >= selectedLeftSnapshotIndex) ? (
                    <button id={snapshot.snapshot_id.toString() === right_snapshot_id ? 'Selected-Item' : null}
                            onClick={() => handleRightSnapClick(snapshot.snapshot_id, index)}>
                      {snapshot.date_modified}
                    </button>
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