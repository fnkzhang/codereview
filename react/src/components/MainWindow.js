import React from "react";
import { useParams } from "react-router";
import ReviewWindow from "./ReviewWindow";
import SnapshotSelector from "./SnapshotSelector";

export default function MainWindow() {

  const {document_id, snapshot_id} = useParams()

  return(
    <div>
      <SnapshotSelector/>
      <ReviewWindow/>
    </div>
  )
}