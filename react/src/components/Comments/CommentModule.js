import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getAllCommentsForDocument } from '../../api/APIUtils.js';
import { useEffect } from 'react';
import { useParams } from 'react-router';

function CommentModule ({ moduleLineJump, leftSnapshotId, rightSnapshotId, snapshotId, 
  start , end, comments, setComments, userData, editorLanguage, editorCode, 
  checkIfCanGetLLMCode, getHighlightedCode, updateHighlightedCode, commitState}) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [newComment, setNewComment] = useState('');

  const {document_id} = useParams()

  const [userDataLocal] = useState(userData);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        let allComments = []
        let commentResults =  await getAllCommentsForDocument(document_id)

        allComments = allComments.concat(commentResults)


        setComments(allComments)
        
      } catch (error) {
        console.log(error)
      } finally {
        setCommentsLoading(false)
      }
    }

    if (commentsLoading === true) {
      fetchData()
    }
  }, [commentsLoading, leftSnapshotId, rightSnapshotId, document_id, setComments])

  function handleCommentFieldChange (event) {
    setNewComment(event.target.value);
  };

  async function handleNewCommentSubmit() {
    try {
      if (snapshotId !== null) {

        // ToDo Handle Nested Comments in future
        let createdComment = await createComment(snapshotId, userDataLocal.email, 0, newComment, start.column, start.lineNumber, end.column, end.lineNumber)
        
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
          comments={comments.sort((a, b) => {
            // First, compare by boolean
            if (a.is_resolved !== b.is_resolved) {
              // If boolean component is not equal, sort by boolean component
              return a.is_resolved ? 1 : -1;
            } else {
              // If boolean component is equal, sort by date
              return (new Date(b.date_modified)) - (new Date(a.date_modified));
            }
          }).filter((comment) => {
            return ((comment.snapshot_id === leftSnapshotId) || 
              (comment.snapshot_id === rightSnapshotId))
          })}
          listLineJump={moduleLineJump}
          editorLanguage={editorLanguage}
          editorCode={editorCode}
          checkIfCanGetLLMCode={checkIfCanGetLLMCode}
          getHighlightedCode={getHighlightedCode}
          updateHighlightedCode={updateHighlightedCode}
          commitState={commitState}
          userData={userData}
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