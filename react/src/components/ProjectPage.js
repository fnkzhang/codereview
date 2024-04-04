import React, { useState, useEffect} from "react"
import { useNavigate, useParams } from "react-router"
import { getProjectDocuments, getAllSnapshotsFromDocument } from "../api/APIUtils"

export default function ProjectPage() {

  const [projectDocuments, setProjectDocuments] = useState([])
  const { project_id } = useParams()
  const navigate = useNavigate()

  // Grab Documents if logged in and userdata
  useEffect(() => {

    // Grab User Data
    async function grabProjectData() {
      const docArray = await getProjectDocuments(project_id)
      console.log(docArray)
      setProjectDocuments(docArray)
    } 
    grabProjectData()

  }, [])

  // Clicking on project will redirect to project page to select documents
  async function handleDocumentClick (id, name) {
    const result = await getAllSnapshotsFromDocument(id)
    if (result.success)
      navigate(`/Document/${id}/${result.body[0].snapshot_id}/${result.body[0].snapshot_id}`)
  }
  function DocumentDisplayBox({id, name}) {
    console.log(id, name)
    return (
      <div onClick={() => handleDocumentClick(id, name)} style={{display: "flex", border: "solid white 2px", justifyContent: "center"}}>
        <h4 style={{color: "white", margin:"5px"}}>{id}</h4>
        <h4 style={{color: "white", margin:"5px"}}>{name}</h4>
      </div>
    )
  }

  function DisplayDocumentBox() {
    if(projectDocuments.length > 0) {
      return (
        <div>
          {
            projectDocuments.map((document, index) => {
              return (< DocumentDisplayBox key={index} id={document.doc_id} name={document.name}/> )
            })
          }
        </div>
      )
    }

    return <p>EMPTY</p>
  }


  return (
    <div>
      <div>
        <h3 style={{color: "white", margin:"5px", fontSize:"50px"}}>Project: {project_id}</h3>
      </div>

      <DisplayDocumentBox/>
    </div>
    
  )
}