import React from 'react';
import SubComment from './SubComment.js';

/**
 * SubCommentList component to display a list of subcomments.
 *
 * @component
 * @example
 * // Example usage:
 * const subcomments = [
 *   { author: "Jane Doe", text: "This is a comment." },
 *   { author: "John Doe", text: "This is another comment." }
 * ];
 * <SubCommentList subcomments={subcomments} />
 *
 * @param {object} props - Component props
 * @param {Array<{author: string, text: string}>} props.subcomments - Array of subcomment objects
 */
function SubCommentList ( props ) {
  if (props.subcomments != null) {
    return(
      <div>
        {props.subcomments.map((subcomment, index) => (
          <SubComment key={index} author={subcomment.author} text={subcomment.text} />
        ))}
      </div>
    )
  } else {
    return
  }
}

export default SubCommentList;