import React from 'react';
import Comment from './Comments.js';

const Comment_list = ({ comments }) => (
  <div>
    {comments.map((comment, index) => (
      <Comment key={index} author={comment.author} text={comment.text} />
    ))}
  </div>
);

export default Comment_list;