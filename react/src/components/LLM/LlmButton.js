import React, { useEffect } from "react";


export default function LlmButton( { editorLanguage, editorCode, checkIfCanGetLLMCode, getHighlightedCode,
  highlightStartX, highlightStartY, highlightEndX, highlightEndY } ) {
  
  useEffect(() => {

  }, [])

  const handleCreateSuggestion = async () => {
    // Popup new suggestion
    console.log(editorLanguage, editorCode  , checkIfCanGetLLMCode());
    console.log(getHighlightedCode(highlightStartX, highlightStartY, highlightEndX, highlightEndY));
  }

  
  return (
    <div>
      <button className="border border-alternative border-1 px-2 py-1 ml-1 w-full transition duration-300 hover:bg-altBackground rounded"
      onClick={handleCreateSuggestion}>
        Create LLM Suggestion
      </button>
    </div>

  )
}