import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { getAllProjectActiveCommentsForLatestCommit, getLatestCommitForProject } from "../../api/APIUtils";
import { Card } from "flowbite-react"
import { Tooltip } from "react-tooltip";
import { REVIEW_STATE } from "../../utils/reviewStateMapping";

export default function ProjectDisplayBox({id, name, author, date}) {
  // Clicking on project will redirect to project page to select documents
  // Enum For State
  const [reviewState, setReviewState] = useState(REVIEW_STATE.CLOSED) 
  const [isLoaded, setIsLoaded] = useState(false)
  const [latestCommitApproveCount, setLatestCommitApproveCount] = useState(0)
  const [activeSuggestionCount, setActiveSuggestionCount] = useState(0)


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
        if(latestCommit.approved_count !== null)
          setLatestCommitApproveCount(latestCommit.approved_count)
      }

      setIsLoaded(true)
    }

    getLatestCommitState(id)
  }, [id])

  // Get All Active Comments for Commit
  useEffect(() => {
    async function getAllActiveCommentsForLatestProjectCommit(project_id) {
      let response = await getAllProjectActiveCommentsForLatestCommit(project_id)

      setActiveSuggestionCount(response.length)
    }
    getAllActiveCommentsForLatestProjectCommit(id)
  }, [id])
  const handleProjectClick = async (project_id) => {
    navigate(`/Project/${project_id}/Commit/0`)
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
        data-tooltip-id={`${id}`}
        onClick={() => handleProjectClick(id)}
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
          <div className="flex flex-1 text-2xl justify-end h-9 ">
            <h1 className={"align-middle pr-5 " + stateColor}>{reviewState.toString().toUpperCase()}</h1>
            {latestCommitApproveCount !== 0 ? 
              <h3 className="bg-[#47FF5D] pl-2 pr-2 rounded-sm rounded-tl-[10px]">
                {latestCommitApproveCount}
              </h3> : null}


            {activeSuggestionCount !== 0 ? 
              <h3 className="bg-[#FFCE83] pl-2 pr-2 rounded-sm rounded-br-[10px]">
                {activeSuggestionCount}
              </h3> : null}

          </div>
        </div>
        <h4 className="text-textcolor p-1">
          <span className="font-bold">Date Modified: </span>
          <span className="block"> {date} </span>
        </h4>
        <Tooltip 
          className="z-9999" 
          id={`${id}`}
          place="bottom"
          disableStyleInjection="true"
          content={
            <div>
              <p>
                {author}/{name}
              </p>
            </div>
          }
        />
      </Card>
    )
  }

  return null
}