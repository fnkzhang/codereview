import React, { useState } from "react";
import { Button, Label, TextInput } from "flowbite-react";
import { createProject } from "../../api/APIUtils";
import { useNavigate } from "react-router";

export default function ProjectCreation() {

  const [projectName, setProjectName] = useState("");
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

  return (
    <div className="flex justify-center mt-20">
      <form className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded">
        <div>
          <div className="mb-5 block">
            <Label className="text-3xl" value="New Project"/>
          </div>
          <div className="mb-3 block">
            <Label className="text-2xl" value="Project Name"/>
          </div>
          <TextInput className="text-black shadow-white" placeholder="Name of Project" sizing="lg" onChange={(e) => setProjectName(e.target.value)} shadow/>
        </div>

        {isError ? (<p className="text-red-600 text-xl">Error: Could Not Create Project</p>) : null}
        <Button onClick={handleCreateProject} className="bg-alternative transition-colors duration-200 hover:bg-slate-500">Create</Button>
      </form>
    </div>
  )
}