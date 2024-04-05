import { resolveComment } from '../../api/APIUtils';
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
      <div className="border border-solid border-alternative border-2 p-2 m-2 text-textcolor text-sm text-left rounded-lg whitespace-pre-wrap">
        <div className="flex">
          <strong className="text-sm font-bold ml-4">{author}</strong>
          <div className="text-offwhite items-right ml-4"><i>~ {date}</i></div>
        </div>
        <div className="mt-2">{text}</div>
        <div className="flex items-center justify-center mt-2">
          <button
            className="border border-alternative border-1 px-2 py-1 w-1/2 transition duration-300 hover:bg-altBackground rounded"
            onClick={() => commentLineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY)}>
            Jump to Line
          </button>
          <button
            className="border border-alternative border-1 px-2 py-1 ml-1 w-1/2 transition duration-300 hover:bg-altBackground rounded"
            onClick={handleResolve}>
            Resolve Comment
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