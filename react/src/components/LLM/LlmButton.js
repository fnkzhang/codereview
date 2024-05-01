import React, { useEffect } from "react";


export default function LlmButton( { fileCode, comment }) {
  
  useEffect(() => {

  }, [])

  const handleCreateSuggestion = () => {
    // Popup new suggestion
    console.log("Clicked")
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