import './Edit_window.css';
import Comment_module from "./Comment_module.js"
import { sendData } from "./../api/APIUtils.js";
import { getCode } from "./../dev/getCode.js";
import Editor, { DiffEditor, useMonaco, loader } from '@monaco-editor/react';
import react, { useState } from 'react';

function Edit_window () {
  //Temp Stuff
  const initial_code = getCode()
  const [code, setCode] = useState(initial_code)

  async function handleClick(e) {
    console.log(code)
    
    await sendData('code', code)
      .then(data => console.log(data))
      .catch((e) => {
        console.log(e)
      })
  }

  function handleChange(newValue) {
    setCode(newValue)
  }

  return (      
    <div className="Edit-window">
      <div className="Code-view">
        <button onClick={handleClick}>Submit Code</button>
        <Editor className="Monaco-editor"
          defaultLanguage="python"
          defaultValue={initial_code}
          onChange={handleChange}
        />
      </div>
      <div className="Comment-view">
        <Comment_module />
      </div>
    </div>)
}

export default Edit_window