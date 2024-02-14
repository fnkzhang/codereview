import React from 'react';
import Comment from './Comments.js';

function CommentList ({ comments, listLineJump }) {
  return(
    <div>
      {comments.map((comment, index) => (
        <Comment 
          key={index}
          commentID={comment.commentID}
          author={comment.author}
          text={comment.text} 
          subcomments={comment.subcomments}
          line={comment.line}
          commentLineJump={listLineJump}
        />
      ))}
    </div>
  )
}

export default CommentList;