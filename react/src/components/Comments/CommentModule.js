import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getCommentsOnSnapshot } from '../../api/APIUtils.js';
import { useEffect } from 'react';

function CommentModule ({ moduleLineJump, leftSnapshotId, rightSnapshotId, snapshotId, 
  start , end, comments, setComments}) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [newComment, setNewComment] = useState('');

  useEffect(() => {
    console.log(leftSnapshotId, rightSnapshotId, comments)

    const fetchData = async () => {
      try {
        let leftSnapshotComments = await getCommentsOnSnapshot(leftSnapshotId)
        let rightSnapshotComments = await getCommentsOnSnapshot(rightSnapshotId)

        console.log(leftSnapshotComments, rightSnapshotComments)

        let commentData = comments
        
        console.log(commentData)
        setComments(commentData)
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

  function handleNewCommentChange (event) {
    setNewComment(event.target.value);
  };

  async function handleNewCommentSubmit (event) {
    event.preventDefault();

    try {
      console.log(snapshotId)
      if (snapshotId != null) {
        console.log("adding comment ...")
        setComments([...comments,{
          author_email: 2,//todo fix email
          comment_id: 1000,
          content: newComment,
          date_created: "time",
          date_modified: "time",
          snapshot_id: snapshotId,
          reply_to_id: 0,
          highlight_start_x: start.column,
          highlight_start_y: start.lineNumber,
          highlight_end_x: end.column,
          highlight_end_y: end.lineNumber
        }])
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
        <form className="Comment-submit-section" onSubmit={handleNewCommentSubmit}>
        <label>Add a new comment:</label>
        <textarea
          rows="4"
          cols="50"
          value={newComment}
          onChange={handleNewCommentChange}
        ></textarea>
        <br />
        <button type="submit">Submit Comment</button>
      </form>
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
      <form className="Comment-submit-section" onSubmit={handleNewCommentSubmit}>
        <label>Add a new comment:</label>
        <textarea
          rows="4"
          cols="50"
          value={newComment}
          onChange={handleNewCommentChange}
        ></textarea>
        <br />
        <button type="submit">Submit Comment</button>
      </form>
    </div>
  );
}

export default CommentModule;