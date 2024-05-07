import React, { userState, useEffect } from "react";

export default function PermissionPage() {


  let [projectName, setProjectName] = useState("")

  useEffect(() => {
    
  }) 
  return (
    <div>
      <h3>Project: {projectName}</h3>
    </div>
  )
}