import './ReviewWindow.css';
import AppHeader from "./AppHeader.js"
import CommentModule from "./Comments/CommentModule.js"
import { sendData } from "../api/APIUtils.js";
import { getCode, getNewCode } from "../dev/getCode.js";
import { DiffEditor, useMonaco } from '@monaco-editor/react';
import { useState } from 'react';

function ReviewWindow() {
  //Temp Stuff
  const initialCode = getCode()
  const [updatedCode, setCode] = useState(getNewCode)
  const [currentLine, setLine] = useState(1)

  async function handleClick() {
    console.log(updatedCode)

    await sendData('updatedCode', updatedCode)
      .then(data => console.log(data))
      .catch((e) => {
        console.log(e)
      })
  }

  function handleChange(newValue) {
    setCode(newValue)
  }

  function lineJump(newLine) {
    setLine(newLine)
  }

  return (
    <div>
      <AppHeader />
      <div className="Review-window">
        <div className="Code-view">
          <button onClick={handleClick}>Submit Code</button>
          <DiffEditor 
            className="Monaco-editor"
            original={initialCode}
            modified={updatedCode}
            originalLanguage="python"
            modifiedLanguage='python'
            onChange={handleChange}
            line={currentLine}
          />
        </div>
        <div className="Comment-view">
          <CommentModule moduleLineJump={lineJump} />
        </div>
      </div>
    </div>
  )
}

export default ReviewWindow