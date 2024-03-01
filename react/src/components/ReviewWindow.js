import './ReviewWindow.css';
import AppHeader from './AppHeader.js';
import Oauth from './Oauth.js';
import CommentModule from './Comments/CommentModule.js';
import { getDoc, createDiff, getDiff } from '../api/APIUtils.js';
import { DiffEditor } from '@monaco-editor/react';
import React, { useState, useRef, useEffect} from 'react';

function ReviewWindow( { originalID, modifiedID } ) {

  const monacoRef = useRef(null);
  const editorRef = useRef(null);
  const [editorReady, setEditorReady] = useState(false);
  const [initialCode, setInit] = useState(null);
  const [updatedCode, setCode] = useState(null); 
  const [currentHighlightStart, setStart] = useState(null);
  const [currentHighlightEnd, setEnd] = useState(null);
  const [editorLoading, setEditorLoading] = useState(true);
  const [snapshotId, setSnapshotID] = useState(null);
  const decorationIdsRefOrig = useRef([]);
  const decorationIdsRefModif = useRef([]);

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
    if (editorRef.current) {
      const originalEditor = editorRef.current.getOriginalEditor();
      const modifiedEditor = editorRef.current.getModifiedEditor();
  
      const handleSelectionChange = (editor, snapshotID) => (e) => {
        const selection = e.selection;
        const startPosition = selection.getStartPosition();
        const endPosition = selection.getEndPosition();
  
        setSnapshotID(snapshotID);
        setStart(startPosition);
        setEnd(endPosition);
      };
      originalEditor.onDidChangeCursorSelection(handleSelectionChange(originalEditor, originalID));
      modifiedEditor.onDidChangeCursorSelection(handleSelectionChange(modifiedEditor, modifiedID));
    }
  }, [ editorRef, modifiedID, originalID, editorReady ])

  async function handleClick() {
    console.log(updatedCode)

    await createDiff('projectid', 'documentid', 'diffid', initialCode, updatedCode)
      .then(data => console.log(data))
      .catch((e) => {
        console.log(e)
      })
  }

  function lineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY) {

    if (editorRef.current) {

      const range = new monacoRef.current.Range(highlightStartY, highlightStartX, highlightEndY, highlightEndX);
      const decoration = { range: range, options: { isWholeLine: false, className: 'highlight-line' } };
      const modifiedEditor = editorRef.current.getModifiedEditor();
      const originalEditor = editorRef.current.getOriginalEditor();

      if (snapshotID === modifiedID) {
        decorationIdsRefOrig.current = originalEditor.deltaDecorations(decorationIdsRefOrig.current, [])
        decorationIdsRefModif.current = modifiedEditor.deltaDecorations(decorationIdsRefModif.current, [decoration]);
        editorRef.current.getModifiedEditor().revealLine(highlightStartY);
      } else {
        decorationIdsRefModif.current = modifiedEditor.deltaDecorations(decorationIdsRefModif.current, []);
        decorationIdsRefOrig.current = originalEditor.deltaDecorations(decorationIdsRefOrig.current, [decoration]);
        editorRef.current.getOriginalEditor().revealLine(highlightStartY);
      }
    }
  }

  if (editorLoading) {
    return (
      <div>
        <AppHeader />
        <Oauth/>
        <div className="Review-window">
          <div className="Code-view">
            <div
              className="Loading-data"
            >
              Loading...
            </div>
          </div>
          <div className="Comment-view">
            <CommentModule
              moduleLineJump={lineJump}
              snapshotId={snapshotId}
              start={currentHighlightStart}
              end={currentHighlightEnd}
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
              editor.getModifiedEditor().updateOptions({
                readOnly: false
              })
              editor.getOriginalEditor().updateOptions({
                readOnly: false
              })

              // Add the onChange event listener to the editor instance
              const onChangeHandler = () => {
                const updatedCode = editor.getModifiedEditor().getValue();
                setCode(updatedCode);
              };

              editor.onDidUpdateDiff(onChangeHandler);

              setEditorReady(true)
            }}
          />
        </div>
        <div className="Comment-view">
          <CommentModule 
            moduleLineJump={lineJump}
            snapshotId={snapshotId}
            start={currentHighlightStart}
            end={currentHighlightEnd}
          />
        </div>
      </div>
    </div>
  )
}

export default ReviewWindow