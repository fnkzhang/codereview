import React from 'react';
import Comment from './Comments.js';

function CommentList ({ comments }) {
  return(
    <div>
      {comments.map((comment, index) => (
        <Comment 
          key={index}
          commentID={comment.commentID}
          author={comment.author}
          text={comment.text} 
          subcomments={comment.subcomments}/>
      ))}
    </div>
  )
}

export default CommentList;