import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument } from "../api/APIUtils";
import getCookie from "../utils/utils";

// todo testing remove later
import Oauth from "./Oauth.js";

export default function SnapshotSelector() { 
    const [snapshots, setSnapshots] = useState([])

    const navivate = useNavigate()

    const {document_id, snapshot_id} = useParams()
    // Get snapshots for document
    useEffect(() => {
      console.log(document_id, snapshot_id)
        const grabSnapshots = async () => {
            let result = await getAllSnapshotsFromDocument(document_id)

            if (result.success)
              setSnapshots(result.body)
        }

        grabSnapshots()
    }, [])

    async function handleClick(selectedSnapshot) {
      console.log(selectedSnapshot)
      navivate(`/Document/${document_id}/${selectedSnapshot}/`)

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
            name: "TestDocument",
            data: "TESTFILECODE WITH CHANGE"
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


    function DisplaySnapshots() {
        console.log(snapshots)
        if(snapshots.length !== 0) {
            return (
              <div>
                <p>ALIVE</p>
                {snapshots.map((snapshot) => { 
                    console.log(snapshot)
                    return <button onClick={() => handleClick(snapshot.snapshot_id)}>test</button>
                })}              
              </div>
          )
         } 
         else {
            return <div>EMPTY</div>
         }
    }
    return (
        <div>
            <button onClick={createProj}>CreateProject</button>
            <button onClick={createSnapshot}>createDocument</button>
            <Oauth/>
            <DisplaySnapshots/>
        </div>
    )
}