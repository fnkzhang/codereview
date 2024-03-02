import React, {useState, useEffect} from "react";
import { useParams } from "react-router";
import { getSnapshotsFromDocument } from "../api/APIUtils";
import getCookie from "../utils/utils";

// todo testing remove later
import Oauth from "./Oauth.js";

export default function SnapshotSelector() { 
    const [snapshots, setSnapshots] = useState([])

    const {document_id, snapshot_id} = useParams()
    // Get snapshots for document
    useEffect(() => {
        const grabSnapshots = async () => {
            let result = await getSnapshotsFromDocument(document_id, snapshot_id)
            console.log(result)

            //setSnapshots(result)
        }

        grabSnapshots()
    }, [])

    function handleClick() {

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
        console.log(typeof(snapshots))
        if(snapshots.length !== 0) {
            snapshots.map((snapshot) => {
            <button onClick={() => handleClick(snapshot.snapshot_id)}>test</button>
            })
         } 
         else {
            return <div>EMPTY</div>
         }
    }
    return (
        <div>
            <button onClick={createProj}>CreateProject</button>
            <button onClick={createDocument}>createDocument</button>
            <Oauth/>
            <DisplaySnapshots/>
        </div>
    )
}