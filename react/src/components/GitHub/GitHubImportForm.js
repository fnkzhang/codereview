import React from "react";
import GitHubStatus from "./GitHubStatus";
import { Label, TextInput, Checkbox } from "flowbite-react";

export default function GitHubImportForm ( props ) {

    if (!props.connected) {
      return(
        <div className="text-textcolor">
          Connect to a GitHub account in order to import a project's contents.
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

    if (!props.importFromGitHub) {
      return (
        <div className="flex mt-3 max-w-md flex-col gap-4" id="checkbox">
          <div className="flex items-center gap-2">
            <Checkbox onChange={(e) => {props.setImportFromGitHub(e.target.checked)}} id="accept"/>
            <Label htmlFor="accept" className="flex">
              Import project contents from GitHub.
            </Label>
          </div>
        </div>
      );
    }

    return (
      <div className="flex mt-3 max-w-md flex-col gap-4" id="checkbox">
        <div className="flex items-center gap-2">
          <Checkbox onChange={(e) => {props.setImportFromGitHub(e.target.checked)}} id="accept" defaultChecked/>
          <Label htmlFor="accept" className="flex">
            Import project contents from GitHub.
          </Label>
        </div>
        <div>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Repository Name"/>
          </div>
          <TextInput className="text-black shadow-white" placeholder="Name of GitHub Repository" sizing="lg" onChange={(e) => props.setGitRepo(e.target.value)} shadow required/>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Branch Name"/>
          </div>
          <TextInput className="text-black shadow-white" placeholder="Name of Branch" sizing="lg" onChange={(e) => props.setRepoBranch(e.target.value)} shadow required/>
        </div>
      </div>
    );
  }