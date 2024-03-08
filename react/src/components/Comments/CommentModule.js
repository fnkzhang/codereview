import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getCommentsOnDiff } from '../../api/APIUtils.js';
import { useEffect } from 'react';

function CommentModule ({ moduleLineJump , diffID }) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [comments, setComments] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [diffId] = useState(diffID) 

  useEffect(() => {
    const fetchData = async () => {
      try {
        const commentData = await getCommentsOnDiff(diffId)
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
  }, [commentsLoading, diffId])

  function handleNewCommentChange (event) {
    setNewComment(event.target.value);
  };

  async function handleNewCommentSubmit (event) {
    event.preventDefault();

    try {
      await createComment(diffId, 1, 0, newComment);
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