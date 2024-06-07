import CommentModule from './Comments/CommentModule.js';
import { getDocSnapshot, getCommitData } from '../api/APIUtils.js';
import { DiffEditor } from '@monaco-editor/react';
import React, { useState, useRef, useEffect} from 'react';
import { useParams, useLocation } from 'react-router';
import { REVIEW_STATE } from "../utils/reviewStateMapping";


/**
 * Component for a review window that displays the editors and the difference between the code
 *
 * @component
 * 
 * @example
  <ReviewWindow
    comments={comments}
    setComments={setComments}
    userData={props.userData}
    latestSnapshotData={snapshots[snapshots.length - 1]}
    editorReady={editorReady}
    setEditorReady={setEditorReady}
    setHasUpdatedCode={setHasUpdatedCode}
    setDataToUpload={setDataToUpload}
    editorLanguage={editorLanguage}
    />
 *
 * @param {object} props - Component props
 * @param {Array} props.comments - Array of all comments for project to display
 * @param {Function} props.setComments - Function to set value of comments
 * @param {object} props.userData - Object that holds user data
 * @param {object} props.latestSnapshotData - Object that holds data for newest snapshot version
 * @param {boolean} props.editorReady - Boolean to determine if the editor is ready to display 
 * @param {Function} props.setEditorReady - Function to set editor ready
 * @param {boolean} props.setHasUpdatedCode - Boolean to see if user as edited code in editor
 * @param {Function} props.setDataToUpload - Function to set the code that will be uploaded
 * @param {string} props.editorLanguage - String that holds the editor's language
 */
export default function ReviewWindow( props ) {
  const monacoRef = useRef(null);
  const editorRef = useRef(null);

  //const [editorReady, setEditorReady] = useState(false);
  const [initialCode, setInit] = useState(null);
  const [updatedCode, setCode] = useState(null);

  const [initialUpdatedCode, setInitialUpdatedCode] = useState(null)

  const [currentHighlightStart, setStart] = useState(null);
  const [currentHighlightEnd, setEnd] = useState(null);
  const [editorLoading, setEditorLoading] = useState(true);
  const [snapshotId, setSnapshotID] = useState(null);
  const [commitState, setCommitState] = useState(null)

  const decorationIdsRefOrig = useRef([]);
  const decorationIdsRefModif = useRef([]);

  const location = useLocation();

  const {project_id, commit_id, document_id, left_snapshot_id, right_snapshot_id} = useParams()

  // Get Code for the 2 editors
  useEffect(() => {
    const fetchData = async () => {
      props.setEditorReady(false)
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
  }, [project_id, document_id, left_snapshot_id, right_snapshot_id, props.setEditorReady, location.state])

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
  }, [ editorRef, left_snapshot_id, right_snapshot_id, props.editorReady, initialUpdatedCode, props.setDataToUpload ])


  // Handle Code Edit Detection For New Snapshot Creation
  useEffect(() => {
    if (initialUpdatedCode === null && updatedCode === null)
      return

    // Matching length but code is different or no change made
    if (initialUpdatedCode.length === updatedCode.length) {

      if(initialUpdatedCode !== updatedCode) {
        console.log("Code Not Same as Initial")
        props.setHasUpdatedCode(true)
        props.setDataToUpload(updatedCode)
      } else {
        props.setHasUpdatedCode(false)
      }
      
      return 
    }

    console.log("Code Not Same as Initial")
    // No matching length and is different
    props.setHasUpdatedCode(true)
    props.setDataToUpload(updatedCode)

  }, [updatedCode, initialUpdatedCode, props.setDataToUpload, props.setHasUpdatedCode])

  // Set Set Commit State
  useEffect(() => {
    if(commitState !== null)
      return;

    const getCommitState = async (commit_id) => {
      const commitState = await getCommitData(commit_id)

      if (commitState === null)
        setCommitState(REVIEW_STATE.CLOSED) // Default State because state is not open
      else
        setCommitState(commitState)

    }

    getCommitState(commit_id)
  }, [commit_id, commitState])

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
    if (left_snapshot_id !== right_snapshot_id)
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
  function updateHighlightedCode(codeToReplace, highlightCodeString) {
    
    setCode(codeToReplace)

  }

  // LEFT AND RIGHT SNAPSHOT MUST BE SAME AND LATEST VERSION
  function checkIfCanGetLLMCode() {
    if (left_snapshot_id !== right_snapshot_id)
      return false

    if (location.state.addSnapshots !== null)
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
              comments={props.comments}
              setComments={props.setComments}
              userData={props.userData}
              editorLanguage={props.editorLanguage}
              editorCode={updatedCode}
              checkIfCanGetLLMCode={checkIfCanGetLLMCode}
              getHighlightedCode={getHighlightedCode}
              updateHighlightedCode={updateHighlightedCode}
              commitState={commitState}
            />
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <div className="w-screen flex text-center">
        <div className="bg-altBackground w-2/3 border border-1 border-solid border-black inline-block">
          <DiffEditor 
            className="Monaco-editor"
            original={initialCode}
            modified={updatedCode}
            originalLanguage={props.editorLanguage}
            modifiedLanguage={props.editorLanguage}
            onMount={(editor, monaco) => {
              // Set Value Because Editor Changes length of the Document after mounting
              setCode(editor.getModifiedEditor().getValue())
              setInitialUpdatedCode(editor.getModifiedEditor().getValue())
              editorRef.current = editor
              monacoRef.current = monaco

              editor.getModifiedEditor().updateOptions({
                // Set True Or False if Matching Right Editor Snapshot
                readOnly: false
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

              props.setEditorReady(true)
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
            comments={props.comments}
            setComments={props.setComments}
            userData={props.userData}
            editorLanguage={props.editorLanguage}
            editorCode={updatedCode}
            hasUpdatedCode={props.hasUpdatedCode}
            checkIfCanGetLLMCode={checkIfCanGetLLMCode}
            getHighlightedCode={getHighlightedCode}
            updateHighlightedCode={updateHighlightedCode}
            // Pass Functions for comments to call
          />
        </div>
      </div>
    </div>
  )
}