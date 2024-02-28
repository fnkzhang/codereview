import './ReviewWindow.css';
import AppHeader from './AppHeader.js';
import Oauth from './Oauth.js';
import CommentModule from './Comments/CommentModule.js';
import { getDoc, createDiff, getDiff } from '../api/APIUtils.js';
import { DiffEditor } from '@monaco-editor/react';
import React, { useState, useRef, useEffect} from 'react';

function ReviewWindow() {

  const monacoRef = useRef(null);
  const editorRef = useRef(null);
  const [initialCode, setInit] = useState(null);
  const [updatedCode, setCode] = useState(null);
  const [currentLine, setLine] = useState(1);
  const [editorLoading, setEditorLoading] = useState(true);
  const decorationIdsRef = useRef([]);
  const diffID = 2;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [doc, diff] = await Promise.all([
          getDoc('projectid', 'documentid'),
          getDiff('projectid', 'documentid', 'diffid')
        ]);
        setInit(doc.blobContents)
        setCode(diff.diffResult)
      } catch (error) {
        console.log(error)
      } finally {
        setEditorLoading(false)
      }
    }

    fetchData()
  }, [])

  useEffect(() => {

    if (editorRef.current && monacoRef.current) {
      const modifiedEditor = editorRef.current.getModifiedEditor();

      const lineNumber = 4;
      const range = new monacoRef.current.Range(lineNumber, 24, lineNumber, 29);
      const decoration = { range: range, options: { isWholeLine: false, className: 'highlight-line' } };

      decorationIdsRef.current = modifiedEditor.deltaDecorations(decorationIdsRef.current, [decoration]);
    }
  }, [monacoRef, editorRef, currentLine, updatedCode])

  async function handleClick() {
    console.log(updatedCode)

    await createDiff('projectid', 'documentid', 'diffid', initialCode, updatedCode)
      .then(data => console.log(data))
      .catch((e) => {
        console.log(e)
      })
  }

  function lineJump(newLine) {
    setLine(newLine)

    if (editorRef.current && editorRef.current.getModifiedEditor) {

      editorRef.current.getModifiedEditor().revealLine(newLine);
    }
  }

  if (editorLoading) {
    return (
      <div>
        <AppHeader />
        <Oauth/>
        <div className="Review-window">
          <div className="Code-view">
            <div className="Loading-data">
              Loading...
            </div>
          </div>
          <div className="Comment-view">
            <CommentModule
              moduleLineJump={lineJump}
              diffID={diffID}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <AppHeader />
      <Oauth/>
      <div className="Review-window">
        <div className="Code-view">
          <button onClick={handleClick}>Submit Code</button>
          <DiffEditor 
            className="Monaco-editor"
            original={initialCode}
            modified={updatedCode}
            originalLanguage="python"
            modifiedLanguage="python"
            onMount={(editor, monaco) => {
              editorRef.current = editor
              monacoRef.current = monaco

              // Add the onChange event listener to the editor instance
              const onChangeHandler = () => {
                const updatedCode = editor.getModifiedEditor().getValue();
                setCode(updatedCode);
              };

              editor.onDidUpdateDiff(onChangeHandler);
            }}
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