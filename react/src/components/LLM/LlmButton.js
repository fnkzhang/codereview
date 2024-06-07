import React from "react";
import { getCodeImplementation } from "../../api/APIUtils";

/**
 * Component for creating a suggestion using the LLM model.
 *
 * @component
 * @example
 * // Example usage:
 * <LlmButton
 *   getHighlightedCode={getHighlightedCode}
 *   updateHighlightedCode={updateHighlightedCode}
 *   editorCode={editorCode}
 *   highlightStartX={highlightStartX}
 *   highlightStartY={highlightStartY}
 *   highlightEndX={highlightEndX}
 *   highlightEndY={highlightEndY}
 *   commentText={commentText}
 *   editorLanguage={editorLanguage}
 * />
 *
 * @param {object} props - Component props
 * @param {Function} props.getHighlightedCode - Function to get highlighted code from the editor
 * @param {Function} props.updateHighlightedCode - Function to update highlighted code in the editor
 * @param {string} props.editorCode - Code content in the editor
 * @param {number} props.highlightStartX - Start column of the highlight
 * @param {number} props.highlightStartY - Start line number of the highlight
 * @param {number} props.highlightEndX - End column of the highlight
 * @param {number} props.highlightEndY - End line number of the highlight
 * @param {string} props.commentText - Text of the comment associated with the highlighted code
 * @param {string} props.editorLanguage - Language of the editor content
 */
export default function LlmButton( props ) {
  
  //TODO Display Error Message When LLM Fails

  /**
   * Handles creating a suggestion using the LLM model.
   */
  const handleCreateSuggestion = async () => {
    let highlightedCode = props.getHighlightedCode(props.highlightStartX, props.highlightStartY, props.highlightEndX, props.highlightEndY)
    let result = await getCodeImplementation(props.editorCode, highlightedCode,
      props.highlightStartY, props.highlightEndY, props.commentText, props.editorLanguage)

      props.updateHighlightedCode(result, highlightedCode);
  }
  
  return (
    <div>
      <button className="border border-alternative border-1 px-2 py-1 mt-4 w-full transition duration-300 hover:bg-altBackground rounded"
      onClick={handleCreateSuggestion}>
        Create LLM Suggestion
      </button>
    </div>
  )
}