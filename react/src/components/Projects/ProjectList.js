import React, {useState, useEffect} from "react";

import { useNavigate } from "react-router";
import { getUserProjects } from "../../api/APIUtils";

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
    const handleProjectClick = (id) => {
      navigate(`/Project/${id}`)
    }

    function ProjectDisplayBox({id, name, author, date}) {
      console.log(id, name)
      return (
        <div 
          className="flex border border-alternative border-2 rounded-lg"
          onClick={() => handleProjectClick(id)}
        >
          <h4 className="text-textcolor w-1/3 p-1 box-border border-r-2 border-alternative">
            <span class="font-bold">Project Name: </span>
            {author}/{name}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1 box-border border-r-2 border-alternative">
            <span class="font-bold">Project ID: </span>
            {id}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1 box-border"><span class="font-bold">Date Modified: </span>{date}</h4>
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

                return(<ProjectDisplayBox
                  key={index} 
                  id={project.proj_id} 
                  name={project.name}
                  author={project.author_email}
                  date={new Date(project.date_modified)
                    .toLocaleDateString("en-US", { 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric', 
                      weekday: 'long',  
                      hour: 'numeric',
                      minute: 'numeric',
                      second: 'numeric',
                      timeZoneName: 'short',
                    })}
                  />)
              })
            }
          </div>
        )
      }

      return <p>No Project Available</p>
    }

    if (loading) {
        return (
            <div>
                <h3 className="text-textcolor text-2xl">Your Projects:</h3>
                <div className="Loading-data">
                    Loading...
                </div>
            </div>
        )
    } else {
        return (
            <div>
                <h3 className="text-textcolor text-2xl m-2">Your Projects:</h3>
    
                <DisplayProjects/>
            </div>
        )
    }
}