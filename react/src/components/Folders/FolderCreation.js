import React, { useState } from "react";
import { Button, Label, TextInput } from "flowbite-react";
import { useNavigate, useParams } from "react-router";
import { createFolder } from "../../api/APIUtils";

export default function FolderCreation() {

  const [folderName, setFolderName] = useState("");

  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const {project_id, parent_folder_id} = useParams();


  const handleCreateFolder = async () =>  {
    console.log(folderName, project_id, parent_folder_id)

    let result = await createFolder(folderName, project_id, parent_folder_id)
    console.log(result)
    
    if (result.success)
      navigate(-1);

    console.log(result)
    setIsError(true)
  }

  return (
    <div className="flex justify-center mt-20">
      <form className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded">
        <div>
          <div className="mb-5 block">
            <Label className="text-3xl" value="New Folder"/>
          </div>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Folder Name"/>
          </div>
          <TextInput className="text-black shadow-white" placeholder="Name of Folder" sizing="lg" onChange={(e) => setFolderName(e.target.value)} shadow/>
        </div>

        {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Folder</p>) : null}
        <Button onClick={handleCreateFolder} className="bg-alternative transition-colors duration-200 hover:bg-slate-500">Create</Button>
      </form>
    </div>
  )
}