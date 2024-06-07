import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { getAllProjectActiveCommentsForLatestCommit, getLatestCommitForProject } from "../../api/APIUtils";
import { Card } from "flowbite-react"
import { Tooltip } from "react-tooltip";
import { REVIEW_STATE } from "../../utils/reviewStateMapping";
import { getColor } from "../../utils/utils";

/**
 * Component to display project information in a box format.
 *
 * @component
 * @example
 * // Example usage:
 * <ProjectDisplayBox id={1} author="JohnDoe" name="MyProject" date="2023-06-01" />
 *
 * @param {object} props - Component props
 * @param {number} props.id - The project ID
 * @param {string} props.author - The author of the project
 * @param {string} props.name - The name of the project
 * @param {string} props.date - The date the project was last modified
 */
export default function ProjectDisplayBox( props ) {

  const [reviewState, setReviewState] = useState(REVIEW_STATE.CLOSED) 
  const [isLoaded, setIsLoaded] = useState(false)
  const [latestCommitApproveCount, setLatestCommitApproveCount] = useState(0)
  const [activeSuggestionCount, setActiveSuggestionCount] = useState(0)
  const navigate = useNavigate()

  /**
   * Fetches the latest commit state for the project.
   */
  useEffect(() => {
    async function getLatestCommitState(project_id){
      const latestCommit = await getLatestCommitForProject(project_id)

      if (latestCommit === null)
        console.log("Failed To get latest commit")
      else {
        setReviewState(latestCommit.state)
        if(latestCommit.approved_count !== null)
          setLatestCommitApproveCount(latestCommit.approved_count)
      }

      setIsLoaded(true)
    }

    getLatestCommitState(props.id)
  }, [props.id])

  /**
   * Fetches all active comments for the latest commit of the project.
   */
  useEffect(() => {
    async function getAllActiveCommentsForLatestProjectCommit(project_id) {
      let response = await getAllProjectActiveCommentsForLatestCommit(project_id)

      setActiveSuggestionCount(response.length)
    }
    getAllActiveCommentsForLatestProjectCommit(props.id)
  }, [props.id])

  /**
   * Handles the click event on the project card.
   */
  const handleProjectClick = async (project_id) => {
    navigate(`/Project/${project_id}/Commit/0`)
  }

  if (isLoaded) {
    let stateColor = getColor(reviewState)
    
    return (
      <Card 
        className="w-1/4 bg-background transition-all duration-300 hover:bg-alternative p-3 m-3"
        data-tooltip-id={`${props.id}`}
        onClick={() => handleProjectClick(props.id)}
      >
        <h4 className="text-textcolor overflow-hidden whitespace-nowrap text-ellipsis p-1">
          <span className="font-bold text-xl">{props.author}/{props.name}</span>
        </h4>
        <div className="flex">
          <div className="flex-1">
            <h4 className="text-textcolor p-1">
              <span className="font-bold block">Project ID: </span>
              <span className="block"> {props.id} </span>
            </h4>
          </div>

          {/* Display Approve / Suggestion numbers */}
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
          <span className="block"> {props.date} </span>
        </h4>
        <Tooltip 
          className="z-9999" 
          id={`${props.id}`}
          place="bottom"
          disableStyleInjection="true"
          content={
            <div>
              <p>
                {props.author}/{props.name}
              </p>
              <div>
                {latestCommitApproveCount !== 0 ? 
                  <h3>
                    {latestCommitApproveCount} Approvals
                  </h3> : null}
                {activeSuggestionCount !== 0 ? 
                  <h3>
                    {activeSuggestionCount} Suggestions
                  </h3> : null}
              </div>
            </div>
          }
        />
      </Card>
    )
  }

  return null
}