import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { getComments } from './../../dev/getComments.js'

function CommentModule () {
  const initial_data = getComments()

  const [comments, setComments] = useState(initial_data);

  return (
    <div>
      <p className="Comment-title">Comment Section</p>
      <div className="Comment-list-container">
        <CommentList comments={comments} />
      </div>
    </div>
  );
}

export default CommentModule;