import './ReviewWindow.css';
import CommentModule from './Comments/CommentModule.js';
import { getDocSnapshot } from '../api/APIUtils.js';
import { DiffEditor } from '@monaco-editor/react';
import React, { useState, useRef, useEffect} from 'react';
import { useParams } from 'react-router';

export default function ReviewWindow({ comments, setComments, userData, snapshots }) {

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

  const {document_id, left_snapshot_id, right_snapshot_id} = useParams()

  useEffect(() => {
    const fetchData = async () => {
      setEditorReady(false)
      setEditorLoading(true)
      try {
        const [left_doc, right_doc] = await Promise.all([
          getDocSnapshot('684153597', document_id, left_snapshot_id),
          getDocSnapshot('684153597', document_id, right_snapshot_id)
        ]);
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
    if (editorRef.current) {
      const originalEditor = editorRef.current.getOriginalEditor();
      const modifiedEditor = editorRef.current.getModifiedEditor();
  
      const handleSelectionChange = (editor, snapshotID) => (e) => {
        const selection = e.selection;
        const startPosition = selection.getStartPosition();
        const endPosition = selection.getEndPosition();
  
        setSnapshotID(Number(snapshotID));
        setStart(startPosition);
        setEnd(endPosition);
      };
      originalEditor.onDidChangeCursorSelection(handleSelectionChange(originalEditor, left_snapshot_id));
      modifiedEditor.onDidChangeCursorSelection(handleSelectionChange(modifiedEditor, right_snapshot_id));
    }
  }, [ editorRef, left_snapshot_id, right_snapshot_id, editorReady ])

  function lineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY) {

    if (editorRef.current) {

      const range = new monacoRef.current.Range(highlightStartY, highlightStartX, highlightEndY, highlightEndX);
      const decoration = { range: range, options: { isWholeLine: false, className: 'highlight-line' } };
      const modifiedEditor = editorRef.current.getModifiedEditor();
      const originalEditor = editorRef.current.getOriginalEditor();

      if (snapshotID === Number(right_snapshot_id)) {
        decorationIdsRefOrig.current = originalEditor.deltaDecorations(decorationIdsRefOrig.current, [])
        decorationIdsRefModif.current = modifiedEditor.deltaDecorations(decorationIdsRefModif.current, [decoration]);
        editorRef.current.getModifiedEditor().revealLine(highlightStartY);
      } 
      if (snapshotID === Number(left_snapshot_id)) {
        decorationIdsRefModif.current = modifiedEditor.deltaDecorations(decorationIdsRefModif.current, []);
        decorationIdsRefOrig.current = originalEditor.deltaDecorations(decorationIdsRefOrig.current, [decoration]);
        editorRef.current.getOriginalEditor().revealLine(highlightStartY);
      }
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
              snapshotId={snapshotId}
              leftSnapshotId={Number(left_snapshot_id)}
              rightSnapshotId={Number(right_snapshot_id)}
              start={currentHighlightStart}
              end={currentHighlightEnd}
              comments={comments}
              setComments={setComments}
              userData={userData}
              snapshots={snapshots}
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
                readOnly: true
              })
              editor.getOriginalEditor().updateOptions({
                readOnly: true
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
            leftSnapshotId={Number(left_snapshot_id)}
            rightSnapshotId={Number(right_snapshot_id)}
            start={currentHighlightStart}
            end={currentHighlightEnd}
            comments={comments}
            setComments={setComments}
            snapshots={snapshots}
          />
        </div>
      </div>
    </div>
  )
}