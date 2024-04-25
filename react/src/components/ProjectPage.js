import React, { useState, useEffect} from "react"
import { useNavigate, useParams } from "react-router"
import { Card } from "flowbite-react"
import { getProjectDocuments, getAllSnapshotsFromDocument, getProjectInfo, getProjectTree } from "../api/APIUtils"

// Display Documents For Project
export default function ProjectPage( props ) {

  const [loading, setLoading] = useState(true)
  const [projectDocuments, setProjectDocuments] = useState([])
  const [projectOwnerEmail, setProjectOwnerEmail] = useState(null)
  const [projectRootFolderID, setProjectRootFolderID] = useState(null)
  const [projectName, setProjectName] = useState(null)

  const { project_id } = useParams()
  const navigate = useNavigate()


  // Grab Documents if logged in and userdata
  useEffect(() => {
    async function grabProjectData() {
      let result = await getProjectInfo(project_id)
      
      setProjectRootFolderID(result.root_folder)
      setProjectOwnerEmail(result.author_email)
      setProjectName(result.name)
    }

    // Grab User Data
    async function grabProjectDocuments() {
      const docArray = await getProjectDocuments(project_id)
      setProjectDocuments(docArray)
    } 

    async function grabProjectTree() {
      const projectTree = await getProjectTree(project_id)
      console.log(projectTree)
    }

    async function fetchData() {
      try {
        await Promise.all([
          grabProjectDocuments(),
          grabProjectData(),
          grabProjectTree()
        ])
      } catch (error) {
        console.log(error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Clicking on project will redirect to project page to select documents
  async function handleDocumentClick (document_id, name) {
    const result = await getAllSnapshotsFromDocument(project_id, document_id)
    if (result.success)
      navigate(`/Project/${project_id}/Document/${document_id}/${result.body[0].snapshot_id}/${result.body[0].snapshot_id}`)
  }

  function DocumentDisplayBox({id, name, date}) {
    return (
      <Card 
        className="max-w-sm transition-all duration-300 hover:bg-alternative p-3 m-3"
        onClick={() => handleDocumentClick(id, name)}
      >
        <h4 className="text-textcolor p-1">
          <span className="font-bold">Document Name: </span>
          {name}
        </h4>
        <h4 className="text-textcolor p-1">
          <span className="font-bold">Document ID: </span>
          {id}
        </h4>
        <h4 className="text-textcolor p-1"><span className="font-bold">Date Modified: </span>{date}</h4>
      </Card>
    )
  }

  function DisplayDocumentBox() {
    if(projectDocuments.length > 0) {
      return (
        <div className="flex flex-wrap">
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
    if (props.userData === null)
      return null

    if (props.userData.email !== projectOwnerEmail)
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
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
        onClick={() => navigate(`/Project/${project_id}/${projectRootFolderID}/Document/Create`)}>Upload Document</button>
      </div>
    )
  }

  function DisplayCreateFolderButton() {
    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
        onClick={() => navigate(`/Project/${project_id}/${projectRootFolderID}/Folder/Create`)}>Create Folder</button>
      </div>
    )
  }

  if( props.isLoggedIn === false ) {
    return (
    <div>
      <div className="m-20 text-center text-textcolor text-2xl">
        You must Log in to view this page.
      </div>
    </div>
    )
  }

  if (loading) {
    return (
      <div>
        <div className="text-textcolor text-center m-20 text-xl">
          Loading...
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex">
        <div>
          <h3 className="text-textcolor text-2xl m-2">{`${projectOwnerEmail}/${projectName}`}</h3>
        </div>

        <DisplayDeleteButton/>
        <DisplayUploadDocumentButton/>
        <DisplayCreateFolderButton/>
      </div>

      <DisplayDocumentBox/>
    </div>
    
  )
}