import React, { useState } from "react";
import GitHubStatus from "../GitHub/GitHubStatus.js";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { createProject, pullFromGitHub } from "../../api/APIUtils";
import { useNavigate } from "react-router";

export default function ProjectExport( props ) {

  const [working, setWorking] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

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
    <div className="flex justify-center mt-20">
      <form className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded">
        <div>
          <div className="mb-5 block">
            <Label className="text-3xl" value="Export Project to GitHub"/>
          </div>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Repository Name"/>
          </div>
          <TextInput className="text-black shadow-white" placeholder="Name of Repository" sizing="lg" shadow/>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Branch Name"/>
          </div>
          <TextInput className="text-black shadow-white" placeholder="Name of Branch" sizing="lg" shadow/>
        </div>

        {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Project</p>) : null}
        <Button className="bg-alternative transition-colors duration-200 hover:bg-slate-500">Export</Button>

        <div className="flex justify-center">
          <LoadingSpinner active={working}/>
        </div>
      </form>
    </div>
  )

}