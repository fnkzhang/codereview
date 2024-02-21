import './CommentModule.css'
import React, { useState } from 'react';
import CommentList  from './CommentList';
import { getComments } from './../../dev/getComments.js'
import { useEffect} from 'react';

function CommentModule ({ moduleLineJump, diffComments }) {
  const [comments, setComments] = useState(getComments());

  useEffect(() => {
    console.log(diffComments)
  }, [diffComments])

  return (
    <div>
      <p className="Comment-title">Comment Section</p>
      <div className="Comment-list-container">
        <CommentList 
          comments={comments}
          listLineJump={moduleLineJump}
        />
      </div>
    </div>
  );
}

export default CommentModule;