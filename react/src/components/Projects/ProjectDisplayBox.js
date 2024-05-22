import { useNavigate } from "react-router";
import { getLatestCommitForProject } from "../../api/APIUtils";
import { Card } from "flowbite-react"

export default function ProjectDisplayBox({id, name, author, date}) {
  // Clicking on project will redirect to project page to select documents
  const navigate = useNavigate()
  const handleProjectClick = async (project_id) => {
    let result = await getLatestCommitForProject(project_id)
    console.log(result);
    if (result === null)
      console.log("Failed To get latest commit")
    else {
      let commit_id = result.commit_id
      navigate(`/Project/${project_id}/Commit/${commit_id}`)
    }
      
  }

  return (
    <Card 
      className="w-1/4 bg-background transition-all duration-300 hover:bg-alternative p-3 m-3"
      onClick={() => handleProjectClick(id)}
    >
      <h4 className="text-textcolor overflow-hidden whitespace-nowrap text-ellipsis p-1">
        <span className="font-bold text-xl">{author}/{name}</span>
      </h4>
      <h4 className="text-textcolor p-1">
        <span className="font-bold block">Project ID: </span>
        <span className="block"> {id} </span>
      </h4>
      <h4 className="text-textcolor p-1">
        <span className="font-bold">Date Modified: </span>
        <span className="block"> {date} </span>
      </h4>
    </Card>
  )
}