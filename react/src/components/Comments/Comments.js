import './Comments.css';
import SubCommentList from './SubCommentList';
import React from 'react';
import { Link } from "react-router-dom"

function Comment ({ commentID, author, text, subcomments }) {
  return (
    <div>
      <div className="Comment-container">
        <strong className="Comment-author">{author}</strong>
        <div className="Comment-text">{text}</div>
        <div className="Comment-details-button">
          <Link to={`/comment/${commentID}`}>
            <button>View Details</button>
          </Link>
        </div>
      </div>
      <div className="Sub-comment-list-container">
        <SubCommentList subcomments={subcomments}/>
      </div>
    </div>
  );
}

export default Comment;