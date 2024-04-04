import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getAllCommentsForDocument } from '../../api/APIUtils.js';
import { useEffect } from 'react';
import { useParams } from 'react-router';

function CommentModule ({ moduleLineJump, leftSnapshotId, rightSnapshotId, snapshotId, 
  start , end, comments, setComments, userData}) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [newComment, setNewComment] = useState('');

  const {document_id, left_snapshot_id, right_snapshot_id} = useParams()

  const [userDataLocal] = useState(userData);
  
  useEffect(() => {
      
    console.log(start, end, comments, document_id)
    //console.log(leftSnapshotId, rightSnapshotId, comments, userDataLocal)

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
  }, [commentsLoading, leftSnapshotId, rightSnapshotId])

  function handleCommentFieldChange (event) {
    setNewComment(event.target.value);
  };

  async function handleNewCommentSubmit() {
    try {
      console.log(snapshotId)
      if (snapshotId != null) {
        console.log("adding comment ...", userDataLocal)

        // ToDo Handle Nested Comments in future
        let createdComment = await createComment(snapshotId, userDataLocal.email, 0, newComment, start.column, start.lineNumber, end.column, end.lineNumber)

        console.log(createdComment)
        
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
        <p className="Comment-title">Comment Section</p>
        <div className="Comment-loading">
          Loading...
        </div>
        <div className="Comment-submit-section">
        <label>Add a new comment:</label>
        <textarea
          rows="4"
          cols="50"
          value={newComment}
          onChange={handleCommentFieldChange}
        ></textarea>
        <br />
        <button type="submit" onClick={handleNewCommentSubmit}>Submit Comment</button>
      </div>
      </div>
    )
  }

  return (
    <div>
      <p className="Comment-title">Comment Section</p>
      <div className="Comment-list-container">
        <CommentList 
          comments={comments.filter(function(comment) {
            return ((comment.snapshot_id === leftSnapshotId) || (comment.snapshot_id === rightSnapshotId)) && (comment.is_resolved === false)
          })}
          listLineJump={moduleLineJump}
        />
      </div>
      <div className="Comment-submit-section">
        <label>Add a new comment:</label>
        <textarea
          rows="4"
          cols="50"
          value={newComment}
          onChange={handleCommentFieldChange}
        ></textarea>
        <br />
        <button type="submit" onClick={handleNewCommentSubmit}>Submit Comment</button>
      </div>
    </div>
  );
}

export default CommentModule;