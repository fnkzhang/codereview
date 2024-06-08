import React from 'react';
import Comment from './Comments.js';

/**
 * CommentList component to display a list of comments.
 *
 * @component
 * @example
 * // Example usage:
 * const comments = [
 *   {
 *     comment_id: 1,
 *     author_email: "user@example.com",
 *     content: "This is a comment.",
 *     subcomments: [],
 *     date_modified: "2024-06-07T12:00:00Z",
 *     snapshot_id: 123,
 *     highlight_start_x: 10,
 *     highlight_start_y: 20,
 *     highlight_end_x: 30,
 *     highlight_end_y: 40,
 *     is_resolved: false
 *   },
 *   // Add more comment objects as needed
 * ];
 * <CommentList
 *   comments={comments}
 *   setCommentsLoading={setCommentsLoading}
 *   listLineJump={listLineJump}
 *   editorLanguage={editorLanguage}
 *   editorCode={editorCode}
 *   checkIfCanGetLLMCode={checkIfCanGetLLMCode}
 *   getHighlightedCode={getHighlightedCode}
 *   updateHighlightedCode={updateHighlightedCode}
 *   commitState={commitState}
 *   userData={userData}
 * />
 *
 * @param {object} props - Component props
 * @param {Array} props.comments - Array of comment objects
 * @param {function} props.setCommentsLoading - Function to set the loading state of comments
 * @param {function} props.listLineJump - Function to jump to the line associated with the comment
 * @param {string} props.editorLanguage - The language of the code editor
 * @param {string} props.editorCode - The code content of the editor
 * @param {function} props.checkIfCanGetLLMCode - Function to check if LLM code can be retrieved
 * @param {function} props.getHighlightedCode - Function to get the highlighted code from the code editor
 * @param {function} props.updateHighlightedCode - Function to update the highlighted code after the LLM is called
 * @param {string} props.commitState - The state of the commit
 * @param {object} props.userData - Data of the logged-in user
 */

function CommentList ( props ) {

  if (!Array.isArray(props.comments)) {
    return null
  }

  return(
    <div>
      {props.comments.map((comment, index) => (
        <Comment 
          setCommentsLoading={props.setCommentsLoading}
          key={index}
          commentID={comment.comment_id}
          author={comment.author_email}
          text={comment.content} 
          subcomments={comment.subcomments}
          date={new Date(comment.date_modified)
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
          snapshotID={comment.snapshot_id}
          commentLineJump={props.listLineJump}
          highlightStartX={comment.highlight_start_x}
          highlightStartY={comment.highlight_start_y}
          highlightEndX={comment.highlight_end_x}
          highlightEndY={comment.highlight_end_y}
          isResolved={comment.is_resolved}
          editorLanguage={props.editorLanguage}
          editorCode={props.editorCode}
          checkIfCanGetLLMCode={props.checkIfCanGetLLMCode}
          getHighlightedCode={props.getHighlightedCode}
          updateHighlightedCode={props.updateHighlightedCode}
          commitState={props.commitState}
          userData={props.userData}
        />
      ))}
    </div>
  )
}

export default CommentList;