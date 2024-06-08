import React from 'react';

/**
 * SubComment component to display an individual comment with the author's name and text.
 *
 * @component
 * @example
 * // Example usage:
 * <SubComment author="Jane Doe" text="This is a comment." />
 *
 * @param {object} props - Component props
 * @param {string} props.author - The name of the comment author
 * @param {string} props.text - The text of the comment
 */
function SubComment ( props ) {
  return (
    <div className="Comment-container">
      <strong className="Comment-author">{props.author}</strong>
      <div className="Comment-text">{props.text}</div>
    </div>
  );
}

export default SubComment;