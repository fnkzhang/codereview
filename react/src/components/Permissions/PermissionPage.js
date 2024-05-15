import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { getProjectInfo, getAllUsersWithPermissionForProject, addUserToProject, removeUserFromProject } from "../../api/APIUtils";
import { Label, TextInput, Button } from "flowbite-react";
import BackButton from "../BackButton";

export default function PermissionPage( props ) {

  let [userToAddEmail, setUserToAddEmail] = useState("");
  let [projectName, setProjectName] = useState("");
  let [projectUsers, setProjectUsers] = useState([]);
  //let [projectAuthorEmail, setProjectAuthorEmail] = useState(null)

  let [isLoading, setIsLoading] = useState(true)
  // Todo Checks user permission value to determine if user can do actions / be on this page

  let [isError, setIsError] = useState(false);
  let [errorString, setErrorString] = useState("");

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
    
    setUserToAddEmail("")
    setProjectUsers([])
    setIsError(false)
    setErrorString("")

    fetchData()

  }, [project_id, props, isLoading]) 


  const handleAddUserEmailToProject = async () => {
    if (!isValidEmailString(userToAddEmail)) {
      setIsError(true)
      setErrorString("Not Valid Email")
      return;
    }

    let result = await addUserToProject(project_id, userToAddEmail, "Editor", 12)

    console.log(result);
    
    if(!result.success  ) {
      setErrorString(result.reason)
      setIsError(true)
      return;
    }

    console.log(result);
    setIsLoading(true)
  }

  const handleRemoveUsersFromProject = async (emailToRemove) => {
    console.log(emailToRemove);
    let result = await removeUserFromProject(project_id, emailToRemove)

    if(!result.success) {
      setIsError(true)
      return;
    }

    console.log(result);
    setIsLoading(true)
  }

  function isValidEmailString(email) {
    console.log(email);
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    console.log(emailRegex.test(email));
    if (emailRegex.test(email))
      return true
    
    return false;
  }
  
  const handleMouseDown = (e) => {
    let button = e.target;
    button.classList.remove("scale-100")
    button.classList.add("scale-110");
  }

  const handleMouseUp = (e) => {
    let button = e.target;
    button.classList.remove("scale-110");
    button.classList.add("scale-100")
  }

  function ProjectUserDisplay({projectUsers, isLoading, props}) {
    return (
      <div>
        <h3 className="text-3xl">Existing Users</h3>
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
      <div >
        <header className="text-textcolor text-3xl">
          <h3 className="ml-[10%] mt-5">Project: {projectName}</h3>
        </header>

        <div className="flex justify-center">
          <section className="max-w-lg w-2/3 shadow-md shadow-[gray] 
            text-textcolor bg-altBackground m-5 mt-16 rounded">
            <div>
              <BackButton/> 
            </div>
            <div className="p-20 pt-10">
              <div className="mb-5">
                <Label className="text-textcolor text-3xl" value="Add Users To The Project"/>
              </div>

              <TextInput className=" text-black shadow-white text-5xl w-full" placeholder="User Email" sizing="lg" 
                onChange={(e) => setUserToAddEmail(e.target.value)} shadow/>

              {isError ? (<p className="text-red-600 text-xl">{errorString}</p>) : null}
              <Button onClick={handleAddUserEmailToProject} className="bg-alternative transition-all duration-200
              mt-5 w-full  hover:bg-slate-500"
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}>Add User</Button>

            </div>

            {/* <Dropdown label=""/> */}
            
          </section>
          
          <aside  className="w/1/3 text-textcolor text-xl float-right bg-altBackground
          m-5 mt-16 p-20 pt-10 rounded shadow-md shadow-[gray] ">
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