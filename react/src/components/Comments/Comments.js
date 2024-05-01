import { resolveComment } from '../../api/APIUtils';
import SubCommentList from './SubCommentList';
import { Card } from "flowbite-react";
import React from 'react';
import LlmButton from '../LLM/LlmButton';

function Comment ({ setCommentsLoading, commentID, author, text, subcomments, date, commentLineJump, snapshotID, latestSnapshotData,
  highlightStartX, highlightStartY, highlightEndX, highlightEndY, isResolved,
  editorLanguage, editorCode, checkIfCanGetLLMCode, getHighlightedCode
}) {
  async function handleResolve() {
    console.log("RESOLVING COMMENT")
    console.log(commentID, author, snapshotID)
    let result = await resolveComment(commentID);

    setCommentsLoading(true)
    console.log(result)

  }

  function Buttons () {
    if (!isResolved) {
      return (
      <div>
        <div className="flex items-center justify-center mt-2">
          <button
            className="border border-alternative border-1 px-2 py-1 ml-1 w-1/2 transition duration-300 hover:bg-altBackground rounded"
            onClick={handleResolve}>
            Resolve Comment
          </button>
          <button
            className="border border-alternative border-1 px-2 py-1 w-1/2 transition duration-300 hover:bg-altBackground rounded"
            onClick={() => commentLineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY)}>
            Jump to Line
          </button>
        </div>

        {latestSnapshotData?.snapshot_id === snapshotID ? (
            <div>
              <LlmButton
                editorLanguage={editorLanguage}
                editorCode={editorCode}
                checkIfCanGetLLMCode={checkIfCanGetLLMCode}
                getHighlightedCode={getHighlightedCode}
                highlightStartX={highlightStartX}
                highlightStartY={highlightStartY}
                highlightEndX={highlightEndX}
                highlightEndY={highlightEndY}
              />
          </div>
        ) : null}
      </div>

      )
    }

     return (
    <div className="flex items-center justify-center mt-2">
      <button
        className="border border-alternative border-1 px-2 py-1 w-full transition duration-300 hover:bg-altBackground rounded"
        onClick={() => commentLineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY)}>
        Jump to Line
      </button>
    </div>)
  }
  
  return (
    <div>
      <Card className={isResolved ? 
        "max-w-full border-solid border-alternative border-2 p-2 m-2 text-textcolor text-sm text-left rounded-lg whitespace-pre-wrap"
        : "max-w-full border-solid border-offwhite border-2 p-2 m-2 text-textcolor text-sm text-left rounded-lg whitespace-pre-wrap"}>
        <div className="flex">
          <strong className="text-sm font-bold ml-4">{author}</strong>
          <div className="text-offwhite items-right ml-4"><i>~ {date}</i></div>
        </div>
        <div className="mt-2">{text}</div>
        <Buttons/> 
      </Card>
      <div className="Sub-comment-list-container">
        <SubCommentList subcomments={subcomments}/>
      </div>
    </div>
  );
}

export default Comment;