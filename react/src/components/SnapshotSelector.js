import React, {useState, useEffect} from "react";
import { useParams } from "react-router";
import { getSnapshotsFromDocument } from "../api/APIUtils";


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
        }

        //grabSnapshots()
    }, [])

    return (
        <div>
            <Oauth/>
        </div>
    )
}