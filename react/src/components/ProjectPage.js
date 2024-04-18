import React, { useState, useEffect} from "react"
import { useNavigate, useParams } from "react-router"
import Oauth from "./Oauth.js"
import { getProjectDocuments, getAllSnapshotsFromDocument, getProjectInfo } from "../api/APIUtils"

// Display Documents For Project
export default function ProjectPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userData, setUserData] = useState(null)

  const [projectDocuments, setProjectDocuments] = useState([])
  const [projectOwnerEmail, setProjectOwnerEmail] = useState(null)

  const { project_id } = useParams()
  const navigate = useNavigate()

  // Grab Documents if logged in and userdata
  useEffect(() => {
    async function grabProjectData() {
      let result = await getProjectInfo(project_id)

      setProjectOwnerEmail(result.author_email)
    }

    // Grab User Data
    async function grabProjectDocuments() {
      const docArray = await getProjectDocuments(project_id)
      console.log(docArray)
      setProjectDocuments(docArray)
    } 
    grabProjectDocuments()

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
            <span className="font-bold">Document Name: </span>
            {name}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1 box-border border-r-2 border-alternative">
            <span className="font-bold">Document ID: </span>
            {id}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1 box-border"><span className="font-bold">Date Modified: </span>{date}</h4>
        </div>
    )
  }

  function DisplayDocumentBox() {
    console.log(projectDocuments)
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

    return (<div className="m-20 text-center text-textcolor text-2xl">
      No Documents In Project.
  </div>)
  }

  function DisplayDeleteButton() {
    console.log(userData, projectOwnerEmail)
    if (userData === null)
      return null

    if (userData.email !== projectOwnerEmail)
      return null

    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:bg-red-800/75 m-1"
        onClick={() => navigate(`/Project/Delete/${project_id}`)}>Delete Project</button>
      </div>
    )
  }
  
  function DisplayUploadDocumentButton() {
    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:bg-red-800/75 m-1"
        onClick={() => navigate(`/Project/${project_id}/Document/Create`)}>Upload Document</button>
      </div>
    )
  }

  return (
    <div>
      <Oauth
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        userData={userData}
        setUserData={setUserData}
      />
      <div className="flex">
        <div>
          <h3 className="text-textcolor text-2xl m-2">Project ID: {project_id}</h3>
        </div>

        <DisplayDeleteButton/>
        <DisplayUploadDocumentButton/>
      </div>

      <DisplayDocumentBox/>
    </div>
    
  )
}