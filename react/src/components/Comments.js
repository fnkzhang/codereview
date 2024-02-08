import "./Comments.css"
import React from 'react';

const Comment = ({ author, text }) => (
  <div className="Comment-container">
    <strong className="Comment-author">{author}</strong>
    <div className="Comment-text">{text}</div>
  </div>
);

export default Comment;