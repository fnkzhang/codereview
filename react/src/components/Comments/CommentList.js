import React from 'react';
import Comment from './Comments.js';

function CommentList ({ comments, listLineJump }) {
  return(
    <div>
      {comments.map((comment, index) => (
        <Comment 
          key={index}
          commentID={comment.comment_id}
          author={comment.author_id}
          text={comment.content} 
          subcomments={comment.subcomments}
          line={1}
          commentLineJump={listLineJump}
        />
      ))}
    </div>
  )
}

export default CommentList;