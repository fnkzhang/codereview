import './Comments.css';
import SubCommentList from './SubCommentList';
import React from 'react';

function Comment ({ commentID, author, text, subcomments, line, commentLineJump }) {
  return (
    <div>
      <div className="Comment-container">
        <strong className="Comment-author">{author}</strong>
        <div className="Comment-text">{text}</div>
        <div className="Comment-details-button">
          <button onClick={() => commentLineJump(line)}>
            Jump to Line
          </button>
        </div>
      </div>
      <div className="Sub-comment-list-container">
        <SubCommentList subcomments={subcomments}/>
      </div>
    </div>
  );
}

export default Comment;