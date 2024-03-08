import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getCommentsOnSnapshot } from '../../api/APIUtils.js';
import { useEffect } from 'react';

import { getComments } from '../../dev/getComments.js'

function CommentModule ({ moduleLineJump, leftSnapshotId, rightSnapshotId, snapshotId, start , end}) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  //const [comments, setComments] = useState(null);
  const [comments, setComments] = useState(getComments())
  const [newComment, setNewComment] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        //const commentData = await getCommentsOnDiff(snapshotID)
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
  }, [commentsLoading])

  function handleNewCommentChange (event) {
    setNewComment(event.target.value);
  };

  async function handleNewCommentSubmit (event) {
    event.preventDefault();

    try {
      //await createComment(snapshotId, 1, 0, newComment);
      setComments([...comments,{
        author_id: 1,
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
          comments={comments}
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