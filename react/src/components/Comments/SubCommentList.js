import React from 'react';
import SubComment from './SubComment.js';

function SubCommentList ({ subcomments }) {
  if (subcomments != null) {
    return(
      <div>
        {subcomments.map((subcomment, index) => (
          <SubComment key={index} author={subcomment.author} text={subcomment.text} />
        ))}
      </div>
    )
  } else {
    return
  }
}

export default SubCommentList;