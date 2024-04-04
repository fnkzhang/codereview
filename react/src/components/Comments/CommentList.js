import React from 'react';
import Comment from './Comments.js';

function CommentList ({ setCommentsLoading, comments, listLineJump }) {
  if (!Array.isArray(comments)) {
    return null
  }

  return(
    <div>
      {comments.map((comment, index) => (
        <Comment 
        setCommentsLoading={setCommentsLoading}
          key={index}
          commentID={comment.comment_id}
          author={comment.author_email}
          text={comment.content} 
          subcomments={comment.subcomments}
          date={comment.date_modified}
          snapshotID={comment.snapshot_id}
          commentLineJump={listLineJump}
          highlightStartX={comment.highlight_start_x}
          highlightStartY={comment.highlight_start_y}
          highlightEndX={comment.highlight_end_x}
          highlightEndY={comment.highlight_end_y}
        />
      ))}
    </div>
  )
}

export default CommentList;