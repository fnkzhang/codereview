import React, { useState } from "react";
import LoadingSpinner from "../Loading/LoadingSpinner";
import { Button, Label, TextInput } from "flowbite-react";
import { useNavigate, useParams } from "react-router";
import { createFolder } from "../../api/APIUtils";
import BackButton from "../BackButton";

export default function FolderCreation( props ) {

  const [folderName, setFolderName] = useState("");
  const [working, setWorking] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const {project_id, commit_id, parent_folder_id} = useParams();


  const handleCreateFolder = async (e) =>  {
    e.preventDefault() // Prevent form submission

    setWorking(true)

    let result = await createFolder(folderName, project_id, commit_id, parent_folder_id)
    
    if (result.success) {
      navigate(`/Project/${project_id}/`)
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

  return (
    <div>
      <div>
        <BackButton/>
      </div>
      <div className="flex justify-center mt-20">
        <form
          className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded"
          onSubmit={handleCreateFolder}
        >
          <div>
            <div className="mb-5 block">
              <Label className="text-3xl" value="New Folder"/>
            </div>
            <div className="mb-3 block">
              <Label className="text-2xl" value="Folder Name"/>
            </div>
            <TextInput className="text-black shadow-white" placeholder="Name of Folder" sizing="lg" onChange={(e) => setFolderName(e.target.value)} shadow required/>

            {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Folder</p>) : null}
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