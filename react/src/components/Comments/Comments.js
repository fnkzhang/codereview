import { resolveComment } from '../../api/APIUtils';
import SubCommentList from './SubCommentList';
import { Card, Spinner } from "flowbite-react";
import React, { useEffect, useState } from 'react';
import LlmButton from '../LLM/LlmButton';
import LoadingSpinner from '../Loading/LoadingSpinner';

function Comment ({ setCommentsLoading, commentID, author, text, subcomments, date, commentLineJump, snapshotID,
  highlightStartX, highlightStartY, highlightEndX, highlightEndY, isResolved,
  editorLanguage, editorCode, checkIfCanGetLLMCode, getHighlightedCode, updateHighlightedCode,
  commitState, userData
}) {

  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(()=> {
    if (userData === undefined)
      return

    setIsLoaded(true)
    
  }, [userData])

  async function handleResolve() {
    console.log("RESOLVING COMMENT")
    console.log(commentID, author, snapshotID)
    let result = await resolveComment(commentID);

    setCommentsLoading(true)
    console.log(result)

  }

  // Show Resolve Button only for Author
  function ShowResolveButton({ userData, commentAuthor }) {
    if(userData.email !== commentAuthor)
      return null
    
    return (
      <button
        className="flex-1 border border-alternative border-1 px-2 py-1 ml-1 transition duration-300 hover:bg-altBackground rounded"
        onClick={handleResolve}>
        Resolve Comment
      </button>
    )
  }

  function Buttons ({commitState, userData, commentAuthor}) {
    if (!isResolved) {
      return (
      <div>
        <div className="flex items-center justify-center mt-2">
          <ShowResolveButton userData={userData} commentAuthor={commentAuthor}/>
          <button
            className="flex-1 border border-alternative border-1 px-2 py-1 transition duration-300 hover:bg-altBackground rounded"
            onClick={() => commentLineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY)}>
            Jump to Line
          </button>
        </div>

        {checkIfCanGetLLMCode() ? (
            <div>
              <LlmButton
                editorLanguage={editorLanguage}
                editorCode={editorCode}
                commentText={text}
                checkIfCanGetLLMCode={checkIfCanGetLLMCode}
                getHighlightedCode={getHighlightedCode}
                highlightStartX={highlightStartX}
                highlightStartY={highlightStartY}
                highlightEndX={highlightEndX}
                highlightEndY={highlightEndY}
                updateHighlightedCode={updateHighlightedCode}
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

  if (isLoaded) {
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
  
          <Buttons commitState={commitState} userData={userData} commentAuthor={author}/> 
  
        </Card>
        <div className="Sub-comment-list-container">
          <SubCommentList subcomments={subcomments}/>
        </div>
      </div>
    );
  }

  return (
    <div className='flex justify-center'>
      <LoadingSpinner active={true}/>
    </div>
  )


}

export default Comment;