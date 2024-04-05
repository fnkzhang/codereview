import React, { useState } from 'react';
import CommentList  from './CommentList';
import { createComment, getAllCommentsForDocument } from '../../api/APIUtils.js';
import { useEffect } from 'react';
import { useParams } from 'react-router';

function CommentModule ({ moduleLineJump, leftSnapshotId, rightSnapshotId, snapshotId, 
  start , end, comments, setComments, userData}) {
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [newComment, setNewComment] = useState('');

  const {document_id, left_snapshot_id, right_snapshot_id} = useParams()

  const [userDataLocal] = useState(userData);
  
  useEffect(() => {
    console.log(start, end, comments, document_id)

    const fetchData = async () => {
      try {
        let allComments = []
        let commentResults =  await getAllCommentsForDocument(document_id)
        console.log(commentResults)

        allComments = allComments.concat(commentResults)


        setComments(allComments)
        
      } catch (error) {
        console.log(error)
      } finally {
        setCommentsLoading(false)
      }
    }

    if (commentsLoading === true) {
      fetchData()
    }
  }, [commentsLoading, leftSnapshotId, rightSnapshotId])

  useEffect(() => {
    console.log("comment Updated")
  }, [comments])

  function handleCommentFieldChange (event) {
    setNewComment(event.target.value);
  };

  async function handleNewCommentSubmit() {
    try {
      console.log(snapshotId)
      if (snapshotId != null) {
        console.log("adding comment ...", userDataLocal)

        // ToDo Handle Nested Comments in future
        let createdComment = await createComment(snapshotId, userDataLocal.email, 0, newComment, start.column, start.lineNumber, end.column, end.lineNumber)

        console.log(createdComment)
        
        setCommentsLoading(true);
      }
    } catch (error) {
      console.log(error);
    } finally {
      setNewComment('')
    }
  };

  function filterComments() {

    if (comments.length > 0)
      return comments.filter((comment) => {
        console.log(comment)
        return ((comment.snapshot_id === leftSnapshotId) || (comment.snapshot_id === rightSnapshotId)) && (comment.is_resolved === false)
      })
    
    return []
  }

  if (commentsLoading) {
    return (
      <div>
        <p className="text-textcolor text-center text-xl">Comment Section</p>
        <div className="text-textcolor text-center text-xl h-70vh">
          Loading...
        </div>
        <div className="Comment-submit-section">
        <label className="text-textcolor">Add a new comment:</label>
        <textarea
          className="border border-alternative rounded-md px-4 py-2 focus:outline-none focus:border-blue-500 w-full h-1/5"
          type="text"
          value={newComment}
          onChange={handleCommentFieldChange}
        ></textarea>
        <br />
        <button className="text-textcolor" type="submit" onClick={handleNewCommentSubmit}>Submit Comment</button>
      </div>
      </div>
    )
  }

  return (
    <div>
      <p className="text-textcolor text-center text-xl">Comment Section</p>
      <div className="overflow-y-scroll h-70vh">
        <CommentList 
          setCommentsLoading={setCommentsLoading}
          comments={comments.filter((comment) => {
            return ((comment.snapshot_id === leftSnapshotId) || (comment.snapshot_id === rightSnapshotId)) && (comment.is_resolved === false)
          })}
          listLineJump={moduleLineJump}
        />
      </div>
      <div className="Comment-submit-section">
        <label className="text-textcolor">Add a new comment:</label>
        <textarea
          className="border border-alternative rounded-md px-4 py-2 focus:outline-none focus:border-blue-500 w-full h-1/5"
          type="text"
          value={newComment}
          onChange={handleCommentFieldChange}
        ></textarea>
        <br />
        <button className="text-textcolor" type="submit" onClick={handleNewCommentSubmit}>Submit Comment</button>
      </div>
    </div>
  );
}

export default CommentModule;