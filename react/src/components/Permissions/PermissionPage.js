import React, { useState, useEffect } from "react";
import { useParams } from "react-router";
import { getProjectInfo, getAllUsersWithPermissionForProject, addUserToProject } from "../../api/APIUtils";
import { Label, TextInput, Button, Dropdown } from "flowbite-react";
export default function PermissionPage( props ) {

  let [userToAddEmail, setUserToAddEmail] = useState("");
  let [projectName, setProjectName] = useState("");
  let [projectUsers, setProjectUsers] = useState([]);
  let [projectAuthorEmail, setProjectAuthorEmail] = useState(null)

  // Todo Checks user permission value to determine if user can do actions / be on this page

  let [isError, setIsError] = useState(false);
  let [canRemoveUsers, setCanRemoveUsers] = useState(false);

  const {project_id} = useParams();

  // Set Data For Page on Load
  useEffect(() => {
    if (!props.isLoggedIn)
      return;

    const getProjectData = async () => {
      let projectData = await getProjectInfo(project_id);
      //console.log(projectData.author_email, props.userData.email, projectData.author_email === props.userData.email);
      if (projectData.author_email === props.userData.email)
        setCanRemoveUsers(true);

      setProjectName(projectData.name);
    }

    const getCurrentProjectUsers = async () => {
      let projectUserResponse = await getAllUsersWithPermissionForProject(project_id)
      setProjectUsers(projectUserResponse)
      console.log(projectUserResponse);
    }

    getProjectData()
    getCurrentProjectUsers()
  }, [project_id, props.isLoggedIn]) 


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

  if(props.isLoggedIn)
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
              {projectUsers.map((user, index) => {
                return (
                  <div className="flex justify-end m-2" key={user.name + " " + index}>
                    <li className="border rounded-md p-4 mr-1" >
                      {user.name} : {user.userRole}
                    </li>
                    {canRemoveUsers ? (                    
                      <button className="bg-alternative transition-colors duration-200
                          hover:bg-slate-500 rounded text-md p-1">
                      Remove
                    </button> ) : (null)}

                 </div>
                )
              })}    
            </ul>
          </aside>
        </div>

      </div>
    )

  return(
    <div>
      <div className="m-20 text-center text-textcolor text-2xl">
        You must Log in to view this page.
      </div>
    </div>
  )
}