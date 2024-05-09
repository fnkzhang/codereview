import React, { useState, useEffect } from "react";
import { useParams } from "react-router";
import { getProjectInfo, getAllUsersWithPermissionForProject, addUserToProject } from "../../api/APIUtils";
import { Label, TextInput, Button, Dropdown } from "flowbite-react";

export default function PermissionPage() {

  let [userToAddEmail, setUserToAddEmail] = useState("");
  let [projectName, setProjectName] = useState("");
  let [projectUsers, setProjectUsers] = useState([]);

  let [isError, setIsError] = useState(false);

  const {project_id} = useParams();

  // Set Data For Page on Load
  useEffect(() => {
    const getProjectData = async () => {
      let projectData = await getProjectInfo(project_id);
      setProjectName(projectData.name);
    }

    const getCurrentProjectUsers = async () => {
      let projectUserResponse = await getAllUsersWithPermissionForProject(project_id)
      setProjectUsers(projectUserResponse)
      console.log(projectUserResponse);
    }

    getProjectData()
    getCurrentProjectUsers()
  }, [project_id]) 

  const handleAddUserEmailToProject = async () => {
    if (!isValidEmailString(userToAddEmail)) {
      setIsError(true)
      return;
    }

    let result = await addUserToProject(project_id, userToAddEmail, "OwnerPart2", 12)

    if(!result.success)
      setIsError(true)

    console.log(result);
  }

  function isValidEmailString(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (emailRegex.test(email))
      return true
    
    return false;
  }

  return (
    <div>
      <header className="text-textcolor text-5xl">
        <h3 className="ml-[10%] mt-5">Project: {projectName}</h3>
      </header>

      <div className="flex justify-center">
        <section className="max-w-lg w-2/3 
          text-textcolor bg-altBackground m-5 mt-16 p-20 pt-10 rounded">
          <div className="mb-5">
            <Label className="text-textcolor text-3xl" value="Add Users To The Project"/>
          </div>

          <TextInput className=" text-black shadow-white text-5xl w-full" placeholder="User Email" sizing="lg" 
            onChange={(e) => setUserToAddEmail(e.target.value)} shadow/>

          {isError ? (<p className="text-red-600 text-xl">Could not add user to project</p>) : null}
          <Button onClick={handleAddUserEmailToProject} className="bg-alternative transition-colors duration-200
          mt-5 w-full  hover:bg-slate-500">Add User</Button>

          {/* <Dropdown label=""/> */}
        </section>

        <aside  className="w/1/3 text-textcolor text-2xl float-right bg-altBackground
          m-5 mt-16 p-20 pt-10 rounded">
          <h3>Existing Users</h3>
          <ul>
            {projectUsers.map((user) => {
              return <li className="border rounded-md p-4 m-2" key={user.name}>{user.name} : {user.userRole}</li>
            })}      
          </ul>
        </aside>
      </div>

    </div>
  )
}