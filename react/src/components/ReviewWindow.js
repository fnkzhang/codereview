import CommentModule from './Comments/CommentModule.js';
import { getDocSnapshot } from '../api/APIUtils.js';
import { DiffEditor } from '@monaco-editor/react';
import React, { useState, useRef, useEffect} from 'react';
import { useParams } from 'react-router';

export default function ReviewWindow({ comments, setComments, userData, latestSnapshotData, setHasUpdatedCode, setDataToUpload, editorLanguage}) {
  const monacoRef = useRef(null);
  const editorRef = useRef(null);

  const [editorReady, setEditorReady] = useState(false);
  const [initialCode, setInit] = useState(null);
  const [updatedCode, setCode] = useState(null);

  const [initialUpdatedCode, setInitialUpdatedCode] = useState(null)

  const [currentHighlightStart, setStart] = useState(null);
  const [currentHighlightEnd, setEnd] = useState(null);
  const [editorLoading, setEditorLoading] = useState(true);
  const [snapshotId, setSnapshotID] = useState(null);

  const decorationIdsRefOrig = useRef([]);
  const decorationIdsRefModif = useRef([]);

  const {project_id, document_id, left_snapshot_id, right_snapshot_id} = useParams()

  // Get Code for the 2 editors
  useEffect(() => {
    const fetchData = async () => {
      setEditorReady(false)
      setEditorLoading(true)
      try {
        const [left_doc, right_doc] = await Promise.all([
          getDocSnapshot(project_id, document_id, left_snapshot_id),
          getDocSnapshot(project_id, document_id, right_snapshot_id)
        ]);
        setInit(left_doc.body)
        setCode(right_doc.body)
        setInitialUpdatedCode(right_doc.body)
        
      } catch (error) {
        console.log(error)
      } finally {
        setEditorLoading(false)
      }
    }

    fetchData()
  }, [document_id, left_snapshot_id, right_snapshot_id])

  // 
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


  // Handle Code Edit Detection For New Snapshot Creation
  useEffect(() => {
    if (initialUpdatedCode === null && updatedCode === null)
      return

    // Matching length but code is different or no change made
    if (initialUpdatedCode.length === updatedCode.length) {

      if(initialUpdatedCode !== updatedCode) {
        console.log("Code Not Same as Initial")
        setHasUpdatedCode(true)
        setDataToUpload(updatedCode)
      } else {
        setHasUpdatedCode(false)
      }
      
      return 
    }

    console.log("Code Not Same as Initial")
    // No matching length and is different
    setHasUpdatedCode(true)
    setDataToUpload(updatedCode)

  }, [updatedCode])

  function lineJump(snapshotID, highlightStartX, highlightStartY, highlightEndX, highlightEndY) {

    if (editorRef.current) {

      const range = new monacoRef.current.Range(highlightStartY, highlightStartX, highlightEndY, highlightEndX);
      const decoration = { range: range, options: { isWholeLine: false, className: 'bg-highlight' } };
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

  /**
   * 
   * @param {int} highlightStartX 
   * @param {int} highlightStartY 
   * @param {int} highlightEndX 
   * @param {int} highlightEndY 
   * @returns {string}
   */
  function getHighlightedCode(highlightStartX, highlightStartY, highlightEndX, highlightEndY) {
    if (left_snapshot_id != right_snapshot_id)
      return ""

    if (left_snapshot_id != latestSnapshotData?.snapshot_id?.toString())
      return ""
    
    let originalEditor = editorRef.current

    const range = {
      startLineNumber: highlightStartY,
      startColumn: highlightStartX,
      endLineNumber: highlightEndY,
      endColumn: highlightEndX
    };

    if (originalEditor === null)
      return
    
    return originalEditor.getOriginalEditor().getModel().getValueInRange(range)
  }

  // LEFT AND RIGHT SNAPSHOT MUST BE SAME AND LATEST VERSION
  function checkIfCanGetLLMCode() {
    if (left_snapshot_id != right_snapshot_id)
      return false

    if (left_snapshot_id != latestSnapshotData?.snapshot_id?.toString())
      return false

    return true
  }

  if (editorLoading) {
    return (
      <div>
        <div className="h-9/10 w-screen flex text-center">
          <div className="bg-altBackground w-2/3 border border-1 border-solid border-black inline-block">
            <div className="text-textcolor text-center m-20 text-xl">
              Loading...
            </div>
          </div>
          <div className="inline-block w-1/3">
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
            />
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <div className="h-9/10 w-screen flex text-center">
        <div className="bg-altBackground w-2/3 border border-1 border-solid border-black inline-block">
          <DiffEditor 
            className="Monaco-editor"
            original={initialCode}
            modified={updatedCode}
            originalLanguage={editorLanguage}
            modifiedLanguage={editorLanguage}
            onMount={(editor, monaco) => {
              // Set Value Because Editor Changes length of the Document after mounting
              setCode(editor.getModifiedEditor().getValue())
              setInitialUpdatedCode(editor.getModifiedEditor().getValue())

              editorRef.current = editor
              monacoRef.current = monaco
              editor.getModifiedEditor().updateOptions({
                // Set True Or False if Matching Right Editor Snapshot
                readOnly: latestSnapshotData?.snapshot_id?.toString() === right_snapshot_id ? false : true
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
        <div className="inline-block w-1/3">
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
            latestSnapshotData={latestSnapshotData}
            editorLanguage={editorLanguage}
            editorCode={updatedCode}
            checkIfCanGetLLMCode={checkIfCanGetLLMCode}
            getHighlightedCode={getHighlightedCode}
            // Pass Functions for comments to call
          />
        </div>
      </div>
    </div>
  )
}