import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getCommentsOnSnapshot } from '../../api/APIUtils.js';
import { useEffect } from 'react';
import { useRevalidator } from 'react-router';

function CommentModule ({ moduleLineJump, leftSnapshotId, rightSnapshotId, snapshotId, 
  start , end, comments, setComments, userData}) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [newComment, setNewComment] = useState('');


  const [userDataLocal] = useState(userData);

  useEffect(() => {
    console.log(start, end, comments)
    //console.log(leftSnapshotId, rightSnapshotId, comments, userDataLocal)

    const fetchData = async () => {
      try {
        let leftSnapshotComments = await getCommentsOnSnapshot(leftSnapshotId)
        let rightSnapshotComments = await getCommentsOnSnapshot(rightSnapshotId)

        console.log(leftSnapshotComments, rightSnapshotComments)

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
  }, [commentsLoading, leftSnapshotId, rightSnapshotId])

  function handleCommentFieldChange (event) {
    setNewComment(event.target.value);
  };

  async function handleNewCommentSubmit() {
    try {
      console.log(start, end, userData)
      console.log(snapshotId)
      if (snapshotId != null) {
        console.log("adding comment ...", userDataLocal)

        // ToDo Handle Nested Comments in future
        let createdComment = await createComment(snapshotId, userDataLocal.email, 0, newComment, start.column, start.lineNumber, end.column, end.lineNumber)

        console.log(createdComment)
        
        // ToDo Handle hightling x and y handling not sure right now
        // Append Current Comment to Comments

        // setComments([...comments,{
        //   author_email: createdComment["snapshot_id"],
        //   comment_id: createdComment["comment_id"],
        //   content: createdComment["newComment"],
        //   date_created: createdComment["date_created"],
        //   date_modified: createdComment["date_modified"],
        //   snapshot_id: createdComment["snapshotId"],
        //   reply_to_id: createdComment["reply_to_id"],
        //   highlight_start_x: createdComment["highlight_start_x"],
        //   highlight_start_y: createdComment["highlight_start_y"],
        //   highlight_end_x: createdComment["highlight_end_x"],
        //   highlight_end_y: createdComment["highlight_end_y"],
        //   is_resolved: createdComment["is_resolved"]
        // }])

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