import React, { useState, useEffect} from "react"
import { useNavigate, useParams } from "react-router"
import Oauth from "./Oauth.js"
import { getProjectDocuments, getAllSnapshotsFromDocument } from "../api/APIUtils"

export default function ProjectPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userData, setUserData] = useState(null)

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
  function DocumentDisplayBox({id, name, date}) {
    console.log(id, name)
    return (
      <div 
        onClick={() => handleDocumentClick(id, name)} 
        className="flex border border-alternative border-2 rounded-lg m-1"
      >
          <h4 className="text-textcolor w-1/3 p-1 box-border border-r-2 border-alternative">
            <span class="font-bold">Document Name: </span>
            {name}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1 box-border border-r-2 border-alternative">
            <span class="font-bold">Document ID: </span>
            {id}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1 box-border"><span class="font-bold">Date Modified: </span>{date}</h4>
        </div>
    )
  }

  function DisplayDocumentBox() {
    if(projectDocuments.length > 0) {
      return (
        <div>
          {
            projectDocuments.map((document, index) => {
              return (<DocumentDisplayBox 
                key={index} 
                id={document.doc_id} 
                name={document.name}
                date={new Date(document.date_modified)
                  .toLocaleDateString("en-US", { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric', 
                    weekday: 'long',  
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                    timeZoneName: 'short',
                  })}
              /> )
            })
          }
        </div>
      )
    }

    return <p>EMPTY</p>
  }


  return (
    <div>
      <Oauth
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        userData={userData}
        setUserData={setUserData}
      />
      <div>
        <h3 className="text-textcolor text-2xl m-2">Project ID: {project_id}</h3>
      </div>

      <DisplayDocumentBox/>
    </div>
    
  )
}