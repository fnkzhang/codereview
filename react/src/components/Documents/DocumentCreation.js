import React, { useState } from "react";

import { Button, Label, FileInput } from "flowbite-react";

import { useNavigate, useParams } from "react-router";

import { createDocument } from "../../api/APIUtils";
export default function DocumentCreation() {

  const [documentName, setDocumentName] = useState("");
  const [documentData, setDocumentData] = useState("");

  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const {project_id, parent_folder_id} = useParams();


  const handleCreateDocument = async () =>  {
    console.log(documentName, project_id, documentData, parent_folder_id)

    //Todo handle folder in future
    let result = await createDocument(documentName, project_id, documentData, parent_folder_id)
    console.log(result)
    
    if (result.success)
      navigate(-1);

    console.log(result)
    setIsError(true)
  }


  const handleFileUpload = async (e) => {
    let fileText;

    let fileInformation = e.target.files[0];

    setDocumentName(fileInformation.name.split(".")[0])

    console.log(fileInformation)

    let fileReader = new FileReader();

    // Run After Finished Reading File
    fileReader.onloadend = () => {
      fileText = fileReader.result
      console.log(fileText)
      
      setDocumentData(fileText);
    }

    fileReader.readAsText(fileInformation);

  }

  return (
    <div className="flex justify-center mt-20">
      <form className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded">
        <div>
          <div className="mb-5 block">
            <Label className="text-3xl" value="New Document"/>
          </div>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Upload Code File"/>
          </div>
          <FileInput helperText="Text File Containing Code" onChange={handleFileUpload} />
        </div>

        {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Document For File</p>) : null}
        <Button onClick={handleCreateDocument} className="bg-alternative transition-colors duration-200 hover:bg-slate-500">Upload Document</Button>
      </form>
    </div>
  )
}