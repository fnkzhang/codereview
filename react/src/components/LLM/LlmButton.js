import React from "react";
import { getCodeImplementation } from "../../api/APIUtils";


export default function LlmButton( { editorLanguage, editorCode, commentText, checkIfCanGetLLMCode, getHighlightedCode,
  highlightStartX, highlightStartY, highlightEndX, highlightEndY, updateHighlightedCode } ) {
  
  //Todo Display Error Message When LLM Fails
  // const [isError, setIsError] = useState(false)

  const handleCreateSuggestion = async () => {

    let highlightedCode = getHighlightedCode(highlightStartX, highlightStartY, highlightEndX, highlightEndY)
    let result = await getCodeImplementation(editorCode, highlightedCode,
      highlightStartY, highlightEndY, commentText, editorLanguage)

    updateHighlightedCode(result, highlightedCode);
  }

  //const DisplayErroMessage()
  
  return (
    <div>
      <button className="border border-alternative border-1 px-2 py-1 mt-4 w-full transition duration-300 hover:bg-altBackground rounded"
      onClick={handleCreateSuggestion}>
        Create LLM Suggestion
      </button>
    </div>

  )
}