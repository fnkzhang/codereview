import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react";
import LlmButton from "../components/LLM/LlmButton";
import { getCodeImplementation } from "../api/APIUtils";

jest.mock("../api/APIUtils", () => ({
  getCodeImplementation: jest.fn(),
}));

describe("LlmButton", () => {
  it("calls getCodeImplementation when button is clicked", async () => {
    const editorLanguage = "javascript";
    const editorCode = "function helloWorld() {\n  console.log('Hello, world!');\n}";
    const commentText = "Example comment";
    const checkIfCanGetLLMCode = jest.fn();
    const getHighlightedCode = jest.fn().mockReturnValue("console.log('Hello, world!');");
    const highlightStartX = 0;
    const highlightStartY = 0;
    const highlightEndX = 10;
    const highlightEndY = 0;
    const updateHighlightedCode = jest.fn();

    const expectedResult = "LLM code suggestion";

    getCodeImplementation.mockResolvedValueOnce(expectedResult);

    const { getByText } = render(
      <LlmButton
        editorLanguage={editorLanguage}
        editorCode={editorCode}
        commentText={commentText}
        checkIfCanGetLLMCode={checkIfCanGetLLMCode}
        getHighlightedCode={getHighlightedCode}
        highlightStartX={highlightStartX}
        highlightStartY={highlightStartY}
        highlightEndX={highlightEndX}
        highlightEndY={highlightEndY}
        updateHighlightedCode={updateHighlightedCode}
      />
    );

    fireEvent.click(getByText("Create LLM Suggestion"));

    expect(getHighlightedCode).toHaveBeenCalledWith(
      highlightStartX,
      highlightStartY,
      highlightEndX,
      highlightEndY
    );

    expect(getCodeImplementation).toHaveBeenCalledWith(
      editorCode,
      "console.log('Hello, world!');",
      highlightStartY,
      highlightEndY,
      commentText,
      editorLanguage
    );

    await waitFor(() => {
      expect(updateHighlightedCode).toHaveBeenCalledWith(expectedResult, "console.log('Hello, world!');");
    });
  });
});