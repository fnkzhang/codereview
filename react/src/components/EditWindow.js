import './EditWindow.css';
import AppHeader from "./AppHeader.js"
import CommentModule from "./Comments/CommentModule.js"
import { sendData } from "../api/APIUtils.js";
import { getCode } from "../dev/getCode.js";
import Editor from '@monaco-editor/react';
import { useState } from 'react';


import Oauth from './Oauth.js';
function EditWindow() {
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
    <div>
      <AppHeader />
      <Oauth/>
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
          <CommentModule />
        </div>
      </div>
    </div>
  )
}

export default EditWindow