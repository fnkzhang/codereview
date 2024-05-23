import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { getLatestCommitForProject } from "../../api/APIUtils";
import { Card } from "flowbite-react"
import { REVIEW_STATE } from "../../utils/reviewStateMapping";

export default function ProjectDisplayBox({id, name, author, date}) {
  // Clicking on project will redirect to project page to select documents
  // Enum For State
  const [reviewState, setReviewState] = useState(REVIEW_STATE.CLOSED) 
  const [latestCommitIdForReview, setLatestCommitIdForReview] = useState(0)
  const [isLoaded, setIsLoaded] = useState(false)

  const navigate = useNavigate()
  // Get Latest Commit State
  useEffect(() => {
    async function getLatestCommitState(project_id){
      const latestCommit = await getLatestCommitForProject(project_id)

      console.log(latestCommit);
      if (latestCommit === null)
        console.log("Failed To get latest commit")
      else {
        setReviewState(latestCommit.state)
        setLatestCommitIdForReview(latestCommit.commit_id)
      }

      setIsLoaded(true)
    }

    getLatestCommitState(id)
  }, [id])

  const handleProjectClick = async (project_id, commit_id) => {
    navigate(`/Project/${project_id}/Commit/${commit_id}`)
  }
  if (isLoaded) {
    let stateColor = 'text-textcolor';
    // Determine Text Color
    if (reviewState === REVIEW_STATE.OPEN)
      stateColor = 'text-reviewOpen'
    else if (reviewState === REVIEW_STATE.REVIEWED)
      stateColor = 'text-reviewReviewed'
    else
      stateColor = 'text-reviewClosed'

    return (
      <Card 
        className="w-1/4 bg-background transition-all duration-300 hover:bg-alternative p-3 m-3"
        onClick={() => handleProjectClick(id, latestCommitIdForReview)}
      >
        <h4 className="text-textcolor overflow-hidden whitespace-nowrap text-ellipsis p-1">
          <span className="font-bold text-xl">{author}/{name}</span>
        </h4>
        <div className="flex">
          <div className="flex-1">
            <h4 className="text-textcolor p-1">
              <span className="font-bold block">Project ID: </span>
              <span className="block"> {id} </span>
            </h4>
          </div>
          <div className={"flex-1 text-2xl content-center justify-end " + stateColor }>
            <h1>{reviewState.toString().toUpperCase()}</h1>
          </div>
        </div>
        <h4 className="text-textcolor p-1">
              <span className="font-bold">Date Modified: </span>
              <span className="block"> {date} </span>
            </h4>
      </Card>
    )
  }

  return null
}