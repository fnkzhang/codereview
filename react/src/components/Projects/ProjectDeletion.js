import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";

import { Button, Label, TextInput } from "flowbite-react";
import { deleteProject, getProjectInfo } from "../../api/APIUtils";
import Oauth from "../Oauth";

export default function ProjectDeletion() {

    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [userData, setUserData] = useState(null)
    
    const [projectName, setProjectName] = useState("") // Actual Project Name to compare
    const [inputProjectName, setInputProjectName] = useState("") // Handle Input for project name
    const [isError, setIsError] = useState(false);

    const {project_id} = useParams()
    const navigate = useNavigate()

    useEffect(() => {
        async function getProjectData() {
            let result = await getProjectInfo(project_id)

            console.log(result);
            setProjectName(result.name)

        }

        getProjectData();
    }, [project_id])

    const handleDeleteProjectButtonClick = async() => {
        if (inputProjectName !== projectName) {
            console.log("INPUT DOESNT MATCH", inputProjectName, projectName)
            return
        }

        let result = await deleteProject(project_id);
        console.log(result)

        if (result.success)
            navigate("/") // Go Home
        else 
            setIsError(true)
    }

    return (
        <div className="flex justify-center mt-20">
              <Oauth
                isLoggedIn={isLoggedIn}
                setIsLoggedIn={setIsLoggedIn}
                userData={userData}
                setUserData={setUserData}
              />
        <form className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded">
            <div>
                <div className="mb-3 block">
                    <Label className="text-2xl" value="Are you sure you want to delete this project?"/>
                </div>

                <div className="mb-3 block">
                    <Label className="text-2xl">Please type <strong className="text-red-500">{projectName}</strong> into the text field.</Label>
                </div>
                <TextInput className="text-black shadow-white" placeholder="Name of Project" sizing="lg" onChange={(e) => setInputProjectName(e.target.value)} shadow/>
            </div>

            {isError ? (<p className="text-red-600 text-xl">Error: Could Not Delete Project</p>) : null}
            <Button onClick={handleDeleteProjectButtonClick} className="bg-alternative transition-colors duration-200 hover:bg-red-800/75">Delete</Button>
        </form>
        </div>
    )
}