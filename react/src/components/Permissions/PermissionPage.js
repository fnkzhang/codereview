import React, { useState, useEffect } from "react";
import { useParams } from "react-router";
import { getProjectInfo, getAllUsersWithPermissionForProject, addUserToProject, removeUserFromProject, promoteEmailToProjectOwner } from "../../api/APIUtils";
import { Label, TextInput, Button, Dropdown } from "flowbite-react";
import LoadingSpinner from "../Loading/LoadingSpinner";
import BackButton from "../Buttons/BackButton.js";

/**
 * PermissionPage component manages user permissions within a project.
 * It allows project owners to add, remove, and promote users with different levels of access to the project.
 *
 * @component
 * @example
 * // Example usage:
 * <PermissionPage isLoggedIn={true} userData={{ email: "user@example.com" }}/>
 * 
 * @param {object} props - Component props
 * @param {boolean} props.isLoggedIn - Indicates whether the user is currently logged in.
 * @param {object} props.userData - User data object containing information about the logged-in user.
 */
export default function PermissionPage( props ) {

  let [userToAddEmail, setUserToAddEmail] = useState("");
  let [projectName, setProjectName] = useState(null);
  let [projectUsers, setProjectUsers] = useState([]);
  let [projectAuthorEmail, setProjectAuthorEmail] = useState(null)
  let [isLoading, setIsLoading] = useState(true)
  let [isError, setIsError] = useState(false);
  let [errorString, setErrorString] = useState("");
  let [canRemoveUsers, setCanRemoveUsers] = useState(false);
  const {project_id} = useParams();

  // TODO Checks user permission value to determine if user can do actions / be on this page

  /**
   * Gets the project data and current project users.
   */
  useEffect(() => {
    if (!props.isLoggedIn)
      return;

    const getProjectData = async () => {
      let projectData = await getProjectInfo(project_id);
      if (projectData.author_email === props.userData.email)
        setCanRemoveUsers(true);

      setProjectAuthorEmail(projectData.author_email);
      setProjectName(projectData.name);
    }

    const getCurrentProjectUsers = async () => {
      let projectUserResponse = await getAllUsersWithPermissionForProject(project_id)
      setProjectUsers(projectUserResponse)
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
    setCanRemoveUsers(false)
    setIsError(false)
    setErrorString("")

    fetchData()

  }, [project_id, props, isLoading]) 

  /**
   *  Handles adding a user to the project.
   */
  const handleAddUserEmailToProject = async (e) => {
    e.preventDefault()
    e.target.reset()
    if (!isValidEmailString(userToAddEmail)) {
      setIsError(true)
      setErrorString("Not Valid Email")
      return;
    }

    let result = await addUserToProject(project_id, userToAddEmail, "Editor", 3)

    console.log(result);
    
    if(!result.success  ) {
      setErrorString(result.reason)
      setIsError(true)
      return;
    }

    console.log(result);
    setIsLoading(true)
  }

  /**
   * Handles removing a user from the project.
   */
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

  /**
   * Handles promoting a user to the owner of the project.
   */
  const handlePromoteToOwner = async (ownerEmail, emailToPromote) => {
    console.log(ownerEmail, emailToPromote);
    let result = await promoteEmailToProjectOwner(project_id, ownerEmail, emailToPromote)
    console.log(result);

    if(!result.success) {

      setIsError(true)
      return;
    }

    setIsLoading(true)
  }

  /**
   * Checks if the provided email is valid.
   */
  function isValidEmailString(email) {
    console.log(email);
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    console.log(emailRegex.test(email));
    if (emailRegex.test(email))
      return true
    
    return false;
  }

  /**
   *  Handles down mouse event for button interactions.
   */
  const handleMouseDown = (e) => {
    let button = e.target;
    button.classList.remove("scale-100")
    button.classList.add("scale-110");
  }

  /**
   *  Handles up mouse event for button interactions.
   */
  const handleMouseUp = (e) => {
    let button = e.target;
    button.classList.remove("scale-110");
    button.classList.add("scale-100")
  }

  /**
   *  Function to display a specific user for a project.
   */
  function ProjectUserDisplay({projectUsers, isLoading, props}) {
    return (
      <div>
        <h3 className="text-3xl">Existing Users</h3>
        <br/>
          {isLoading ? <LoadingSpinner active={true}/> : (
            <ul>
              {projectUsers.map((user, index) => {
                return (
                  <div className="flex justify-stretch m-2" key={user.name + " " + index}>
                    <li className="border rounded-md p-4 mr-1" >
                      {user.name} : {user.userRole}
                    </li>

                    {canRemoveUsers && props.userData.email !== user.user_email ? ( 
                      <Dropdown lablel="" dismissOnClick={false} placement="right" inline className="p-0 m-0">
                        <div className="bg-alternative">
                          <Dropdown.Item onClick={() => handlePromoteToOwner(projectAuthorEmail, user.user_email)}>Promote To Owner</Dropdown.Item>
                          <Dropdown.Item onClick={() => handleRemoveUsersFromProject(user.user_email)}>Remove</Dropdown.Item>
                        </div>

                      </Dropdown>

                    ) : (null)}

                </div>
                )
              })}    
            </ul>
          )}                
      </div>
    )
  }

  if(props.isLoggedIn)
    return (
      <div>
        <div>
          <BackButton
            location={-1}
          /> 
        </div>
        <div >
          <header className="text-textcolor text-3xl">
            <div className="flex align-middle">
              <h3 className="ml-[10%] mt-5">Project:{projectName !== null ? (" " + projectName) : null}</h3>
              <div className="ml-5 mt-7">
                {projectName !== null ?  null : <LoadingSpinner active={true}/> }                
              </div>

            </div>
            

          </header>

          <div className="flex justify-center">
            <section className="max-w-lg w-2/3 shadow-md shadow-[gray] 
              text-textcolor bg-altBackground m-5 mt-16 rounded">

              <form 
                className="p-20 pt-10" 
                onSubmit={handleAddUserEmailToProject}
              >
                <div className="mb-5">
                  <Label className="text-textcolor text-3xl" value="Add Users To The Project"/>
                </div>
            
                <TextInput 
                  className=" text-black shadow-white text-5xl w-full" 
                  placeholder="User Email" 
                  sizing="lg" 
                  onChange={(e) => setUserToAddEmail(e.target.value)} 
                  shadow 
                  required
                />
                  

                {isError ? (<p className="text-red-600 text-xl">{errorString}</p>) : null}
                <Button type="submit" className="bg-alternative transition-all duration-200
                mt-5 w-full  hover:bg-slate-500"
                  onMouseDown={handleMouseDown}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}>Share</Button>

              </form>
              {/* <Dropdown label=""/> */}
              
            </section>
            
            <aside  className="w-1/3 text-textcolor text-xl float-right bg-altBackground
            m-5 mt-16 p-20 pt-10 rounded shadow-md shadow-[gray] ">
              <ProjectUserDisplay projectUsers={projectUsers} isLoading={isLoading} props={props}/>
            </aside>
          </div>
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
