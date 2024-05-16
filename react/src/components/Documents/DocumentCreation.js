import React, { useState } from "react";
import LoadingSpinner from "../Loading/LoadingSpinner";
import { Button, Label, FileInput } from "flowbite-react";
import { useNavigate, useParams } from "react-router";
import { createDocument } from "../../api/APIUtils";
import BackButton from "../BackButton";
export default function DocumentCreation( props ) {

  const [documentName, setDocumentName] = useState("");
  const [documentData, setDocumentData] = useState("");
  const [working, setWorking] = useState(false)
  const [isUploadedFile, setIsUploadedFile] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const {project_id, parent_folder_id} = useParams();


  const handleCreateDocument = async () =>  {

    setWorking(true)

    if (!isUploadedFile)
      return;

    //Todo handle folder in future
    let result = await createDocument(documentName, project_id, documentData, parent_folder_id)
    
    if (result.success) {
      navigate(`/Project/${project_id}/`)
    } else {
      setWorking(false)
      setIsError(true)
    }
  }


  const handleFileUpload = async (e) => {
    let fileText;

    let fileInformation = e.target.files[0];

    setDocumentName(fileInformation.name)

    console.log(fileInformation)

    let fileReader = new FileReader();

    // Run After Finished Reading File
    fileReader.onloadend = () => {
      fileText = fileReader.result
      console.log(fileText)
      
      setDocumentData(fileText);
      setIsUploadedFile(true)
    }

    fileReader.readAsText(fileInformation);

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
        <div className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground rounded">
          <div className="mt-5 p-20 pt-2">
            <div>
              <div className="mb-5 block">
                <Label className="text-3xl" value="New Document"/>
              </div>
              <div className="mb-3 block">
                <Label className="text-2xl" value="Upload Code File"/>
              </div>
              <FileInput helperText="Text File Containing Code" onChange={handleFileUpload} />
            </div>

            {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Document</p>) : null}
            <Button onClick={handleCreateDocument} className="bg-alternative transition-colors duration-200 hover:bg-slate-500 w-full mt-3 mb-3">Upload Document</Button>

            <div className="flex justify-center">
              <LoadingSpinner active={working}/>
            </div>
          </div>
        </div>
      </div>      
    </div>
  )
}