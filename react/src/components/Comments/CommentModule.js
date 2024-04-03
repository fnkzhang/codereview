import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getCommentsOnSnapshot } from '../../api/APIUtils.js';
import { useEffect } from 'react';
import { useRevalidator } from 'react-router';

function CommentModule ({ moduleLineJump, leftSnapshotId, rightSnapshotId, snapshotId, 
  start , end, comments, setComments, userData, snapshots}) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [newComment, setNewComment] = useState('');


  const [userDataLocal] = useState(userData);
  
  useEffect(() => {
    if (snapshots.length <= 0)
      return
      
    console.log(start, end, comments)
    //console.log(leftSnapshotId, rightSnapshotId, comments, userDataLocal)

    const fetchData = async () => {
      try {
        let leftSnapshotComments = await getCommentsOnSnapshot(leftSnapshotId)
        let rightSnapshotComments = await getCommentsOnSnapshot(rightSnapshotId)

        console.log(leftSnapshotComments, rightSnapshotComments, snapshots)


        let allSnapshotComments = []
        
        
        
        if (leftSnapshotId === rightSnapshotId)
          allSnapshotComments = leftSnapshotComments
        else 
          allSnapshotComments = leftSnapshotComments.concat(rightSnapshotComments)

        let existingCommentData = comments
        
        console.log("Existing Comments", existingCommentData)
        console.log("Snapshot Comments", allSnapshotComments) 

        setComments(allSnapshotComments)
        
      } catch (error) {
        console.log(error)
      } finally {
        setCommentsLoading(false)
      }
    }

    if (commentsLoading === true) {
      fetchData()
    }
  }, [commentsLoading, leftSnapshotId, rightSnapshotId, snapshots])

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
            return (comment.snapshot_id === leftSnapshotId) || (comment.snapshot_id === rightSnapshotId)
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