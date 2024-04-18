import { DiffEditor } from '@monaco-editor/react'
import React from 'react';
import { useParams } from 'react-router-dom';
import { getCode, getNewCode } from './../../dev/getCode.js'

const CommentDetail = () => {
  const { commentId } = useParams()
  const originalCode = getCode()
  const newCode = getNewCode()

  return (
    <div className="text-center text-textcolor">
      <h2>Comment Details</h2>
      <p>Comment ID: {commentId}</p>
      <DiffEditor
        height="90vh"
        language="javascript"
        original={originalCode}
        modified={newCode}
        originalLanguage="python"
        modifiedLanguage='python'
      />
    </div>
  );
};

export default CommentDetail;
