import React, { useState } from "react";
import { getCodeImplementation2 } from "../../api/APIUtils";


export default function LlmButton( { editorLanguage, editorCode, commentText, checkIfCanGetLLMCode, getHighlightedCode,
  highlightStartX, highlightStartY, highlightEndX, highlightEndY, updateHighlightedCode } ) {
    
  const [isError, setIsError] = useState(false)

  const handleCreateSuggestion = async () => {  
    if (!checkIfCanGetLLMCode()) {
      setIsError(true)
      return
    }

    let highlightedCode = getHighlightedCode(highlightStartX, highlightStartY, highlightEndX, highlightEndY)
    console.log(highlightedCode)
    let result = await getCodeImplementation2(editorCode, editorLanguage,
      highlightStartY, highlightEndY, commentText)
    console.log(result)

    updateHighlightedCode(result, highlightedCode);
  }

  //const DisplayErroMessage()
  
  return (
    <div>
      <button className="border border-alternative border-1 px-2 py-1 ml-1 w-full transition duration-300 hover:bg-altBackground rounded"
      onClick={handleCreateSuggestion}>
        Create LLM Suggestion
      </button>
    </div>

  )
}