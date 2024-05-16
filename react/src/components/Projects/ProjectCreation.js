import React, { useState } from "react";
import GitHubImportForm from "../GitHub/GitHubImportForm.js";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { createProject, pullFromGitHub } from "../../api/APIUtils";
import { useNavigate } from "react-router";
import BackButton from "../BackButton.js";

export default function ProjectCreation( props ) {

  const [projectName, setProjectName] = useState("");
  const [importFromGitHub, setImportFromGitHub] = useState(false);
  const [gitRepo, setGitRepo] = useState("");
  const [repoBranch, setRepoBranch] = useState("");
  const [working, setWorking] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const handleCreateProject = async (e) => {
    e.preventDefault() // Prevent form submission

    setWorking(true)

    let result = null

    if (importFromGitHub) {
      result = await pullFromGitHub(projectName, gitRepo, repoBranch)
    } else {
      result = await createProject(projectName)
    }

    if (result.success) {
      navigate("/")
    } else {
      setWorking(false)
      setIsError(true)
    }
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

  return(
    <div>
      <div>
        <BackButton/>
      </div>
      <div className="flex justify-center mt-20">
        <form
          className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded"
          onSubmit={handleCreateProject}
        >
          <div>
            <div className="mb-5 block">
              <Label className="text-3xl" value="Create a New Project"/>
            </div>
            <div className="mb-3 block">
              <Label className="text-2xl" value="Project Name"/>
            </div>
            <TextInput className="text-black shadow-white" placeholder="Name of Project" sizing="lg" onChange={(e) => setProjectName(e.target.value)} shadow required/>
            <GitHubImportForm
              connected={props.connected}
              setConnected={props.setConnected}
              importFromGitHub={importFromGitHub}
              setImportFromGitHub={setImportFromGitHub}
              gitRepo={gitRepo}
              setGitRepo={setGitRepo}
              repoBranch={repoBranch}
              setRepoBranch={setRepoBranch}
            />

            {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Project</p>) : null}
            <Button type="submit" className="bg-alternative transition-colors duration-200 hover:bg-slate-500 w-full mt-3 mb-3">Create</Button>

            <div className="flex justify-center">
              <LoadingSpinner active={working}/>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}