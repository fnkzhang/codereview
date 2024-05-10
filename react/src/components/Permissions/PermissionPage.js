import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { getProjectInfo, getAllUsersWithPermissionForProject, addUserToProject, removeUserFromProject } from "../../api/APIUtils";
import { Label, TextInput, Button } from "flowbite-react";

export default function PermissionPage( props ) {

  let [userToAddEmail, setUserToAddEmail] = useState("");
  let [projectName, setProjectName] = useState("");
  let [projectUsers, setProjectUsers] = useState([]);
  //let [projectAuthorEmail, setProjectAuthorEmail] = useState(null)

  let [isLoading, setIsLoading] = useState(true)
  // Todo Checks user permission value to determine if user can do actions / be on this page

  let [isError, setIsError] = useState(false);
  let [canRemoveUsers, setCanRemoveUsers] = useState(false);

  const navigate = useNavigate();
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
    async function fetchData() {
      try {
        await Promise.all([
          getProjectData(),
          getCurrentProjectUsers(),
        ])
      }
      catch (error) {
        console.log(error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()

  }, [project_id, props]) 


  const handleAddUserEmailToProject = async () => {
    if (!isValidEmailString(userToAddEmail)) {
      setIsError(true)
      return;
    }

    let result = await addUserToProject(project_id, userToAddEmail, "Editor", 12)


    if(!result.success) {
      setIsError(true)
      return;
    }

    console.log(result);
    navigate(0)
  }

  const handleRemoveUsersFromProject = async (emailToRemove) => {
    console.log(emailToRemove);
    let result = await removeUserFromProject(project_id, emailToRemove)

    if(!result.success) {
      setIsError(true)
      return;
    }

    console.log(result);
    navigate(0)
  }

  function isValidEmailString(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (emailRegex.test(email))
      return true
    
    return false;
  }
  
  const handleMouseDown = (e) => {
    let button = e.target;
    console.log(button);
    button.classList.remove("scale-100")
    button.classList.add("scale-110");
  }

  const handleMouseUp = (e) => {
    let button = e.target;
    console.log(button);
    button.classList.remove("scale-110");
    button.classList.add("scale-100")
  }

  function ProjectUserDisplay({projectUsers, isLoading, props}) {
    return (
      <div>
        <h3>Existing Users</h3>
        <br/>
        {isLoading ? <h3>Loading</h3> : null}

        <ul>
          {projectUsers.map((user, index) => {
            return (
              <div className="flex justify-stretch m-2" key={user.name + " " + index}>
                <li className="border rounded-md p-4 mr-1" >
                  {user.name} : {user.userRole}
                </li>

                {canRemoveUsers && props.userData.email !== user.user_email ? (                    
                <button className="bg-alternative transition-colors duration-200 hover:bg-red-800/75 rounded text-md p-1" 
                        onClick={() => handleRemoveUsersFromProject(user.user_email)}>
                  Remove
                </button> ) : (null)}

            </div>
            )
          })}    
        </ul>
      </div>
    )
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
            <Button onClick={handleAddUserEmailToProject} className="bg-alternative transition-all duration-200
            mt-5 w-full  hover:bg-slate-500"
              onMouseDown={handleMouseDown}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}>Add User</Button>

            {/* <Dropdown label=""/> */}
            
          </section>
          
          <aside  className="w/1/3 text-textcolor text-2xl float-right bg-altBackground
          m-5 mt-16 p-20 pt-10 rounded">
            <ProjectUserDisplay projectUsers={projectUsers} isLoading={isLoading}props={props}/>
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