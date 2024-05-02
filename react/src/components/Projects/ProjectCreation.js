import React, { useState } from "react";
import GitHubStatus from "../GitHub/GitHubStatus";
import { Button, Label, TextInput, Checkbox } from "flowbite-react";
import { createProject } from "../../api/APIUtils";
import { useNavigate } from "react-router";

export default function ProjectCreation( props ) {

  const [projectName, setProjectName] = useState("");
  const [importFromGitHub, setImportFromGitHub] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const handleCreateProject = async () => {
    console.log(projectName)

    let result = await createProject(projectName)

    if (result.success)
      navigate("/");
    else
      setIsError(true)

    console.log(result)
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

  function ImportFromGitHub () {

    if (!props.connected) {
      return(
        <div className="text-textcolor">
          Connect to a GutHub account in order to import a project's contents.
          <div className="flex items-center justify-center text-center">
            <div className="border border-offwhite border-1 bg-alternative transition-colors 
              duration-200 hover:bg-slate-500 w-1/3 rounded">
              <GitHubStatus
                connected={props.connected}
                setConnected={props.setConnected}
              />
            </div>
          </div>
        </div>
      )
    }

    const handleCheckboxChange = (event) => {
      setImportFromGitHub(event.target.checked); // Update isChecked state with checkbox value
    };

    if (!importFromGitHub) {
      return (
        <div className="flex max-w-md flex-col gap-4" id="checkbox">
          <div className="flex items-center gap-2">
            <Checkbox onChange={handleCheckboxChange} id="accept"/>
            <Label htmlFor="accept" className="flex">
              Import project contents from GitHub.
            </Label>
          </div>
        </div>
      );
    }

    return (
      <div className="flex max-w-md flex-col gap-4" id="checkbox">
        <div className="flex items-center gap-2">
          <Checkbox onChange={handleCheckboxChange} id="accept" defaultChecked/>
          <Label htmlFor="accept" className="flex">
            Import project contents from GitHub.
          </Label>
        </div>
        <div>
          The box is checked.
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center mt-20">
      <form className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded">
        <div>
          <div className="mb-5 block">
            <Label className="text-3xl" value="Create a New Project"/>
          </div>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Project Name"/>
          </div>
          <TextInput className="text-black shadow-white" placeholder="Name of Project" sizing="lg" onChange={(e) => setProjectName(e.target.value)} shadow/>
          <ImportFromGitHub/>
        </div>

        {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Project</p>) : null}
        <Button onClick={handleCreateProject} className="bg-alternative transition-colors duration-200 hover:bg-slate-500">Create</Button>
      </form>
    </div>
  )
}