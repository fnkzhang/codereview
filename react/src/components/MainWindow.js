import React from "react";
import { useParams } from "react-router";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";

export default function MainWindow() {


  const {document_id, left_snapshot_id, right_snapshot_id} = useParams()
  
  return(
    <div>
      <SnapshotSelector/>
      <ReviewWindow/>
    </div>
  )
}