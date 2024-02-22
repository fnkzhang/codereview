import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { getCommentsOnDiff } from '../../api/APIUtils.js';
import { useEffect} from 'react';

function CommentModule ({ moduleLineJump, diffID }) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [comments, setComments] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const commentData = await getCommentsOnDiff(diffID)
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
  }, [commentsLoading, diffID])

  if (commentsLoading) {
    return (
      <div>
        <p className="Comment-title">Comment Section</p>
        <div className="Comment-loading">
          Loading...
        </div>
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
    </div>
  );
}

export default CommentModule;