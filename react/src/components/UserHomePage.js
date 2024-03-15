import React, {useState, useEffect} from "react";
import Oauth from "./Oauth";

import { useNavigate } from "react-router";
import { getUserProjects } from "../api/APIUtils";
export default function UserHomePage() {

    const [isLoggedIn, setIsLoggedIn] = useState(false)

    const [userData, setUserData] = useState(null)

    const [userProjects, setUserProjects] = useState([])

    const navigate = useNavigate()
  
    useEffect(() => {
      if (!isLoggedIn)
        return
      if (userData.length > 0)
        return

      // Grab User Data
      async function grahProjectData() {
        let projArray = await getUserProjects(userData["email"])
        setUserProjects(projArray)
      } 

      grahProjectData()

    }, [isLoggedIn, userData])

    // Clicking on project will redirect to project page to select documents
    const handleProjectClick = (id, name) => {
      navigate(`/Project/${id}`)
    }

    function ProjectDisplayBox({id, name}) {
      console.log(id, name)
      return (
        <div onClick={() => handleProjectClick(id, name)} style={{display: "flex", border: "solid white 2px", justifyContent: "center"}}>
          <h4 style={{color: "white", margin:"5px"}}>{id}</h4>
          <h4 style={{color: "white", margin:"5px"}}>{name}</h4>
        </div>
      )
    }
    function DisplayProjects() {

      if(userProjects.length > 0) {
        return ( 
          <div>
            {
              userProjects.map( (project, index) => {
                if(project === -1)
                  return

                return(<ProjectDisplayBox key={index} id={project["proj_id"]} name={project["name"]}/>)
              })
            }
          </div>
        )
      }

      return <p>No Project Available</p>
    }
    if (isLoggedIn) {
      return (
      <div>
        <Oauth
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
        userData={userData}
        setUserData={setUserData}
        />

        <div>
          <h3>Your Projects</h3>

           <DisplayProjects/>
        </div>
      </div>
      )
    } else {
      return (
        <div>
            <Oauth
            isLoggedIn={isLoggedIn}
            setIsLoggedIn={setIsLoggedIn}
            userData={userData}
            setUserData={setUserData}/>
        </div>
      )
    }
}