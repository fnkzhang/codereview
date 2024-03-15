import React, {useState, useEffect} from "react";

import { useNavigate } from "react-router";
import { getUserProjects } from "../../api/APIUtils";
import "./ProjectList.css"

export default function ProjectList( userData ) {

    const [userProjects, setUserProjects] = useState([])
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate()
  
    useEffect(() => {
      // Grab User Data
      async function grabProjectData() {
        let projArray = await getUserProjects(userData.userData["email"])
        setUserProjects(projArray)
        setLoading(false)
      } 

      grabProjectData()
    }, [userData])

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
                  return null

                return(<ProjectDisplayBox key={index} id={project["proj_id"]} name={project["name"]}/>)
              })
            }
          </div>
        )
      }

      return <p>No Project Available</p>
    }

    if (loading) {
        return (
            <div className="Project-list">
                <h3>Your Projects</h3>
                <div className="Loading-data">
                    Loading...
                </div>
            </div>
        )
    } else {
        return (
            <div className="Project-list">
                <h3>Your Projects</h3>
    
                <DisplayProjects/>
            </div>
        )
    }
}