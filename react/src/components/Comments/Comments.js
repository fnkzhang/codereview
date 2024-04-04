import { resolveComment } from '../../api/APIUtils';
import './Comments.css';
import SubCommentList from './SubCommentList';
import React from 'react';

function Comment ({ setCommentsLoading, commentID, author, text, subcomments, date, commentLineJump, snapshotID, 
  highlightStartX, highlightStartY, highlightEndX, highlightEndY }) {

  async function handleResolve() {
    console.log("RESOLVING COMMENT")
    console.log(commentID, author, snapshotID)
    let result = await resolveComment(commentID);

    setCommentsLoading(true)
    console.log(result)

  }
  
  return (
    <div>
      <div className="Comment-container">
        <div className="Comment-name-date-container">
          <strong className="Comment-author">{author}</strong>
          <div className="Comment-date"><i>~ {date}</i></div>
        </div>
        <div className="Comment-text">{text}</div>
        <div className="Comment-linejump-button">
          <button onClick={() => commentLineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY)}>
            Jump to Line
          </button>
          <button onClick={handleResolve}>
            Resolve
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