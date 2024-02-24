import React from 'react';
import { mapToName } from './../../dev/authorTranslate.js'
import Comment from './Comments.js';

function CommentList ({ comments, listLineJump }) {
  return(
    <div>
      {comments.map((comment, index) => (
        <Comment 
          key={index}
          commentID={comment.comment_id}
          author={mapToName(comment.author_id)}
          text={comment.content} 
          subcomments={comment.subcomments}
          date={comment.date_modified}
          line={1}
          commentLineJump={listLineJump}
        />
      ))}
    </div>
  )
}

export default CommentList;