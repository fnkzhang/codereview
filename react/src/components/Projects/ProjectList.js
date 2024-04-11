import React, {useState, useEffect} from "react";

import { useNavigate } from "react-router";
import { getUserProjects } from "../../api/APIUtils";

import { Card } from "flowbite-react"

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
        <Card 
          className="max-w-sm transition-all duration-300 hover:bg-slate-100 p-3 m-3"
          onClick={() => handleProjectClick(id)}
        >
          <h4 className="text-textcolor w-1/3 p-1">
            <span class="font-bold">Project Name: </span>
            {author}/{name}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1">
            <span class="font-bold">Project ID: </span>
            {id}
          </h4>
          <h4 className="text-textcolor w-1/3 p-1"><span class="font-bold">Date Modified: </span>{date}</h4>
        </Card>
      )
    }
    function DisplayProjects() {

      if(userProjects.length > 0) {
        return ( 
          <div className="flex flex-wrap">
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

      return (<div className="m-20 text-center text-textcolor text-2xl">
        No projects Available.
      </div>)
    }


    return (
        <div>
            <div className="text-textcolor text-xl">
              <button className="p-3 rounded-lg border-2 bg-alternative m-1">Join Project</button>
              <button className="p-3 rounded-lg border-2 bg-alternative m-1">Create Project</button>
            </div>

            <div>
              <h3 className="text-textcolor text-2xl m-2">Your Projects:</h3>
              
              {/* Inline conditional */}
              { loading ? (                
                <div className="text-textcolor text-center m-20 text-xl">
                    Loading...
                </div> 
              ) : ( 
                <DisplayProjects/>
              )}
            </div>

        </div>
    )
}