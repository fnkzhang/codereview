import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getAllCommentsForDocument } from '../../api/APIUtils.js';
import { useEffect } from 'react';
import { useParams } from 'react-router';

/**
 * CommentModule component to handle comments for a document.
 *
 * @component
 * @example
 * // Example usage:
 * <CommentModule
 *   comments={comments}
 *   leftSnapshotId={leftSnapshotId}
 *   rightSnapshotId={rightSnapshotId}
 *   moduleLineJump={moduleLineJump}
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
 * @param {number} props.leftSnapshotId - ID of the left snapshot
 * @param {number} props.rightSnapshotId - ID of the right snapshot
 * @param {function} props.moduleLineJump - Function to jump to the line associated with the comment
 * @param {string} props.editorLanguage - The language of the code editor
 * @param {string} props.editorCode - The code content of the editor
 * @param {function} props.checkIfCanGetLLMCode - Function to check if LLM code can be retrieved
 * @param {function} props.getHighlightedCode - Function to get the highlighted code from the code editor
 * @param {function} props.updateHighlightedCode - Function to update the highlighted code in the code editor
 * @param {string} props.commitState - The state of the commit
 * @param {object} props.userData - Data of the logged-in user
 */
function CommentModule ( props ) {

  const [commentsLoading, setCommentsLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const {document_id} = useParams()
  const [userDataLocal] = useState(props.userData);
  
  /**
   * Fetches all of the comments for a given document
   */
  useEffect(() => {
    const fetchData = async () => {
      try {
        let allComments = []
        let commentResults =  await getAllCommentsForDocument(document_id)

        allComments = allComments.concat(commentResults)


        props.setComments(allComments)
        
      } catch (error) {
        console.log(error)
      } finally {
        setCommentsLoading(false)
      }
    }

    if (commentsLoading === true) {
      fetchData()
    }
  }, [commentsLoading, props.leftSnapshotId, props.rightSnapshotId, document_id, props.setComments])

  /**
   * Updates the Comment field when the user edits it
   */
  function handleCommentFieldChange (event) {
    setNewComment(event.target.value);
  };

  /**
   * Adds a new comment when the user clicks the submit button
   */
  async function handleNewCommentSubmit() {
    try {
      if (props.snapshotId !== null) {

        // TODO Handle Nested Comments
        await createComment(props.snapshotId, userDataLocal.email, 0, newComment, 
          props.start.column, props.start.lineNumber, props.end.column, props.end.lineNumber)
        
        setCommentsLoading(true);
      }
    } catch (error) {
      console.log(error);
    } finally {
      setNewComment('')
    }
  };

  if (commentsLoading) {
    return (
      <div>
        <p className="text-textcolor text-center text-xl">Comment Section</p>
        <div className="text-textcolor text-center text-xl h-70vh">
          Loading...
        </div>
        <div className="Comment-submit-section">
        <label className="text-textcolor">Add a new comment:</label>
        <textarea
          className="border border-alternative rounded-md px-4 py-2 focus:outline-none focus:border-blue-500 w-full h-1/5"
          type="text"
          value={newComment}
          onChange={handleCommentFieldChange}
        ></textarea>
        <br />
        <button className="text-textcolor" type="submit" onClick={handleNewCommentSubmit}>Submit Comment</button>
      </div>
      </div>
    )
  }

  return (
    <div>
      <p className="text-textcolor text-center text-xl">Comment Section</p>
      <div className="overflow-y-scroll h-70vh">
        <CommentList 
          setCommentsLoading={setCommentsLoading}
          comments={props.comments.sort((a, b) => {
            // First, compare by boolean
            if (a.is_resolved !== b.is_resolved) {
              // If boolean component is not equal, sort by boolean component
              return a.is_resolved ? 1 : -1;
            } else {
              // If boolean component is equal, sort by date
              return (new Date(b.date_modified)) - (new Date(a.date_modified));
            }
          }).filter((comment) => {
            return ((comment.snapshot_id === props.leftSnapshotId) || 
              (comment.snapshot_id === props.rightSnapshotId))
          })}
          listLineJump={props.moduleLineJump}
          editorLanguage={props.editorLanguage}
          editorCode={props.editorCode}
          checkIfCanGetLLMCode={props.checkIfCanGetLLMCode}
          getHighlightedCode={props.getHighlightedCode}
          updateHighlightedCode={props.updateHighlightedCode}
          commitState={props.commitState}
          userData={props.userData}
        />
        
      </div>
      <div className="Comment-submit-section">
        <label className="text-textcolor">Add a new comment:</label>
        <textarea
          className="border border-alternative rounded-md px-4 py-2 focus:outline-none focus:border-blue-500 w-full h-1/5"
          type="text"
          value={newComment}
          onChange={handleCommentFieldChange}
        ></textarea>
        <br />
        <button className="text-textcolor border-alternative border-2 m-1 w-full transition duration-300 hover:bg-altBackground rounded"
          type="submit" onClick={handleNewCommentSubmit}>Submit Comment</button>
      </div>
    </div>
  );
}

export default CommentModule;