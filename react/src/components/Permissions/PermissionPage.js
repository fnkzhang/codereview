import React, { useState, useEffect } from "react";
import { useParams } from "react-router";
import { getProjectInfo, getAllUsersWithPermissionForProject } from "../../api/APIUtils";
import { TextInput } from "flowbite-react";

export default function PermissionPage() {


  let [projectName, setProjectName] = useState("");

  let [projectUsers, setProjectUsers] = useState([]);

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
    }

    getProjectData()
    getCurrentProjectUsers()
  }, [project_id]) 


  return (
    <div className="text-textcolor text-2xl">
      <header>
        <h3>Project: {projectName}</h3>
      </header>

      <section>
        <TextInput placeholder="Existing User Email" shadow/>
      </section>

      <aside className="float-right">
        <h3>Existing Users</h3>
        <ul>
          {projectUsers.map((user) => {
            return <li key={user.name}>{user.name}</li>
          })}      
        </ul>
      </aside>
    </div>
  )
}