import React from 'react';

function SubComment ({ author, text }) {
  return (
    <div className="Comment-container">
      <strong className="Comment-author">{author}</strong>
      <div className="Comment-text">{text}</div>
    </div>
  );
}

export default SubComment;