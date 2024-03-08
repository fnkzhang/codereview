import './ReviewWindow.css';
import CommentModule from './Comments/CommentModule.js';
import { getDocSnapshot, createDiff } from '../api/APIUtils.js';
import { DiffEditor } from '@monaco-editor/react';
import React, { useState, useRef, useEffect} from 'react';
import { useParams } from 'react-router';

export default function ReviewWindow() {

  const monacoRef = useRef(null);
  const editorRef = useRef(null);
  const [initialCode, setInit] = useState(null);
  const [updatedCode, setCode] = useState(null);
  const [currentLine, setLine] = useState(1);
  const [editorLoading, setEditorLoading] = useState(true);
  const decorationIdsRef = useRef([]);
  const diffID = 2;

  const {document_id, left_snapshot_id, right_snapshot_id} = useParams()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [left_doc, right_doc] = await Promise.all([
          getDocSnapshot('684153597', document_id, left_snapshot_id),
          getDocSnapshot('684153597', document_id, right_snapshot_id)
        ]);

        console.log(left_doc, right_doc)
        setInit(left_doc.blobContents)
        setCode(right_doc.blobContents)
      } catch (error) {
        console.log(error)
      } finally {
        setEditorLoading(false)
      }
    }

    fetchData()
  }, [document_id, left_snapshot_id, right_snapshot_id])

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