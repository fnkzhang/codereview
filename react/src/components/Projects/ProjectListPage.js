import React, {useState, useEffect} from "react";

import { useNavigate } from "react-router";
import { getUserProjects } from "../../api/APIUtils";
import ProjectDisplayBox from "./ProjectDisplayBox";


export default function ProjectListPage( props ) {

    const [userProjects, setUserProjects] = useState([])
    const [loading, setLoading] = useState(true);
    
    const navigate = useNavigate()

    // Set up state variables
    useEffect(() => {
      // Grab User Data
      async function grabProjectData() {
        let projArray = await getUserProjects(props.userData.email)
        setUserProjects(projArray)
        setLoading(false)
      } 

      grabProjectData()
    }, [props])


    function DisplayProjects() {

      if(userProjects.length > 0) {
        return ( 
          <div className="flex flex-wrap">
            {
              userProjects.sort((a, b) => {
                  // If boolean component is equal, sort by date
                  return (new Date(b.date_modified)) - (new Date(a.date_modified));
                })
                .map( (project, index) => {
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
              <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:bg-alternative m-1"
              onClick={() => navigate("/Project/Create")}>Create Project</button>
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