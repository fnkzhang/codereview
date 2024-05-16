import React, {useState, useEffect} from "react";
import { useNavigate, useParams } from "react-router";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { deleteProject, getProjectInfo } from "../../api/APIUtils";
import BackButton from "../BackButton.js";

export default function ProjectDeletion( props ) {
    
    const [projectName, setProjectName] = useState("") // Actual Project Name to compare
    const [inputProjectName, setInputProjectName] = useState("") // Handle Input for project name
    const [isError, setIsError] = useState(false);
    const [working, setWorking] = useState(false);
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

        setWorking(true)

        if (inputProjectName !== projectName) {
            console.log("INPUT DOESNT MATCH", inputProjectName, projectName)
            return
        }

        let result = await deleteProject(project_id);
        console.log(result)

        if (result.success) {
            navigate("/") // Go Home
        } else {
            setWorking(false)
            setIsError(true)
        }
    }

    if (props.isLoggedIn === false) {
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

                    <div className="flex justify-center">
                        <LoadingSpinner active={working}/>
                    </div>
                </form>
            </div>
        </div>
    )
}