import { resolveComment } from '../../api/APIUtils';
import SubCommentList from './SubCommentList';
import { Card } from "flowbite-react";
import React, { useEffect, useState } from 'react';
import LlmButton from '../LLM/LlmButton';
import LoadingSpinner from '../Loading/LoadingSpinner';

/**
 * Component representing a comment.
 *
 * @component
 * @example
 * // Example usage:
 * <Comment
 *    author="John Doe"
 *    date="2024-06-10"
 *    text="This is a comment."
 *    isResolved={false}
 *    commentID={123}
 *    setCommentsLoading={handleCommentsLoading}
 *    userData={userData}
 *    commentLineJump={handleCommentLineJump}
 *    snapshotID={snapshotID}
 *    highlightStartX={highlightStartX}
 *    highlightStartY={highlightStartY}
 *    highlightEndX={highlightEndX}
 *    highlightEndY={highlightEndY}
 *    editorLanguage="javascript"
 *    editorCode="// Some code"
 *    checkIfCanGetLLMCode={checkIfCanGetLLMCode}
 *    getHighlightedCode={getHighlightedCode}
 *    updateHighlightedCode={updateHighlightedCode}
 *    subcomments={subcomments}
 * />
 *
 * @param {object} props - Component props
 * @param {string} props.author - The author of the comment
 * @param {string} props.date - The date the comment was posted
 * @param {string} props.text - The content of the comment
 * @param {boolean} props.isResolved - Indicates whether the comment is resolved
 * @param {number} props.commentID - The ID of the comment
 * @param {Function} props.setCommentsLoading - Function to set the loading state of comments
 * @param {object} props.userData - Data of the user who made the comment
 * @param {Function} props.commentLineJump - Function to handle jumping to the comment location
 * @param {number} props.snapshotID - The ID of the snapshot the comment is assocaited with
 * @param {number} props.highlightStartX - The starting X coordinate of the highlight
 * @param {number} props.highlightStartY - The starting Y coordinate of the highlight
 * @param {number} props.highlightEndX - The ending X coordinate of the highlight
 * @param {number} props.highlightEndY - The ending Y coordinate of the highlight
 * @param {string} props.editorLanguage - The language of the associated file snapshot
 * @param {string} props.editorCode - The code content of the associated file snapshot
 * @param {Function} props.checkIfCanGetLLMCode - Function to check if LLM code can be retrieved
 * @param {Function} props.getHighlightedCode - Function to get highlighted code
 * @param {Function} props.updateHighlightedCode - Function to update highlighted code after the LLM is called
 * @param {Array} props.subcomments - Array of subcomments associated with the comment
 */
function Comment ( props ) {

  const [isLoaded, setIsLoaded] = useState(false)

  /**
   * Handles loading the comment when ready
   */
  useEffect(()=> {
    if (props.userData === undefined)
      return

    setIsLoaded(true)
    
  }, [props.userData])

  /**
   * Handles resolving the comment.
   */
  async function handleResolve() {
    await resolveComment(props.commentID);

    props.setCommentsLoading(true)
  }

  /**
   * Renders the resolve button only for the author of the comment.
   */
  function ShowResolveButton() {
    if(props.userData.email !== props.author)
      return null
    
    return (
      <button
        className="flex-1 border border-alternative border-1 px-2 py-1 ml-1 transition duration-300 hover:bg-altBackground rounded"
        onClick={handleResolve}>
        Resolve Comment
      </button>
    )
  }

  /**
   * Renders all of the necessary buttons for the comment.
   */
  function Buttons() {
    if (!props.isResolved) {
      return (
      <div>
        <div className="flex items-center justify-center mt-2">
          <ShowResolveButton/>
          <button
            className="flex-1 border border-alternative border-1 px-2 py-1 transition duration-300 hover:bg-altBackground rounded"
            onClick={() => props.commentLineJump(props.snapshotID, props.highlightStartX, props.highlightStartY, props.highlightEndX, props.highlightEndY)}>
            Jump to Line
          </button>
        </div>

        {props.checkIfCanGetLLMCode() ? (
            <div>
              <LlmButton
                editorLanguage={props.editorLanguage}
                editorCode={props.editorCode}
                commentText={props.text}
                checkIfCanGetLLMCode={props.checkIfCanGetLLMCode}
                getHighlightedCode={props.getHighlightedCode}
                highlightStartX={props.highlightStartX}
                highlightStartY={props.highlightStartY}
                highlightEndX={props.highlightEndX}
                highlightEndY={props.highlightEndY}
                updateHighlightedCode={props.updateHighlightedCode}
              />
          </div>
        ) : null}
      </div>

      )
    }

     return (
    <div className="flex items-center justify-center mt-2">
      <button
        className="border border-alternative border-1 px-2 py-1 w-full transition duration-300 hover:bg-altBackground rounded"
        onClick={() => commentLineJump(props.snapshotID, props.highlightStartX, props.highlightStartY, props.highlightEndX, props.highlightEndY)}>
        Jump to Line
      </button>
    </div>)
  }

  if (isLoaded) {
    return (
      <div>
        <Card className={props.isResolved ? 
          "max-w-full border-solid border-alternative border-2 p-2 m-2 text-textcolor text-sm text-left rounded-lg whitespace-pre-wrap"
          : "max-w-full border-solid border-offwhite border-2 p-2 m-2 text-textcolor text-sm text-left rounded-lg whitespace-pre-wrap"}>
          <div className="flex">
            <strong className="text-sm font-bold ml-4">{props.author}</strong>
            <div className="text-offwhite items-right ml-4"><i>~ {props.date}</i></div>
          </div>
          <div className="mt-2">{props.text}</div>
  
          <Buttons/> 
  
        </Card>
        <div className="Sub-comment-list-container">
          <SubCommentList subcomments={props.subcomments}/>
        </div>
      </div>
    );
  }

  return (
    <div className='flex justify-center'>
      <LoadingSpinner active={true}/>
    </div>
  )
}

export default Comment;