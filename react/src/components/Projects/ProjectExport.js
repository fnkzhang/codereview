import React, { useState } from "react";
import { useParams } from "react-router-dom";
import GitHubStatus from "../GitHub/GitHubStatus.js";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { getDeletedDocuments, getProjectDocuments, getAllSnapshotsFromDocument, pushToExistingBranch } from "../../api/APIUtils";
import { useNavigate } from "react-router";
import BackButton from "../BackButton.js";

export default function ProjectExport( props ) {

  const [gitRepo, setGitRepo] = useState("");
  const [repoBranch, setRepoBranch] = useState("");
  const [working, setWorking] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const { project_id } = useParams()

  const handleExportProject = async (e) => {
    e.preventDefault() // Prevent form submission
  
    setWorking(true)

    let deletedDocuments = null
    let documents = null
    let snapshots = []
  
    await getDeletedDocuments(project_id, gitRepo, repoBranch).then((result) => {
      if(!result.success){
        setWorking(false)
        setIsError(true)
        return
      }
      deletedDocuments = result.body
    })
    .then(async () => { await getProjectDocuments(project_id).then(async (result) => {
        documents = result;
        await Promise.all(documents.map(async (element) => {
          const output = await getAllSnapshotsFromDocument(project_id, element.doc_id)
          snapshots.push(Number(output.body.pop().snapshot_id))
        }))
      })
    })
    .then(async () => { await pushToExistingBranch(project_id, gitRepo, repoBranch, deletedDocuments, snapshots, "Automatic commit generated by codereview web-app.").then((result) => {
      if (result.success){
        navigate(`/Project/${project_id}/`)
      } else {
        setWorking(false)
        setIsError(true)
      }
    })})
  }

  if ( props.isLoggedIn === false ) {
    return (
      <div>
        <div className="m-20 text-center text-textcolor text-2xl">
          You must Log in to view this page.
        </div>
      </div>
    )
  }

  if ( props.connected === false ) {
    return(
      <div className="flex justify-center mt-20">
        <form className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded">
          <div>
            <GitHubStatus
              connected={props.connected}
              setConnected={props.setConnected}
            />
          </div>
        </form>
      </div>
    )
  }

  return (
    <div>
      <div>
        <BackButton/>
      </div>
      <div className="flex justify-center mt-20">
        <form 
          className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded"
          onSubmit={handleExportProject}
        >
          <div>
            <div className="mb-5 block">
              <Label className="text-3xl" value="Export Project to GitHub"/>
            </div>
            <div className="mb-3 block">
              <Label className="text-2xl" value="Repository Name"/>
            </div>
            <TextInput className="text-black shadow-white" placeholder="Name of Repository" sizing="lg" onChange={(e) => setGitRepo(e.target.value)} shadow required/>
            <div className="mb-3 block">
              <Label className="text-2xl" value="Branch Name"/>
            </div>
            <TextInput className="text-black shadow-white" placeholder="Name of Branch" sizing="lg" onChange={(e) => setRepoBranch(e.target.value)} shadow required/>
          </div>

          {isError ? (<p className="text-red-600 text-xl">Error: Could Not Export Project</p>) : null}
          <Button type="submit" className="bg-alternative transition-colors duration-200 hover:bg-slate-500">Export</Button>

          <div className="flex justify-center">
            <LoadingSpinner active={working}/>
          </div>
        </form>
      </div>
    </div>
  )

}