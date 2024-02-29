import React, {useState, useEffect} from "react";
import { useParams } from "react-router";

export default function SnapshotSelector({}) { 
    const [snapshots, setSnapshots] = useState([])

    const {document_id, snapshot_id} = useParams()
    // Get snapshots for document
    useEffect(() => {
        console.log(document_id)
        console.log(snapshot_id)
    }, [])

    return (
        <div>

        </div>
    )
}