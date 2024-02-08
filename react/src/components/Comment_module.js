import "./Comment_module.css"
import React, { useState } from 'react';
import Comment_list  from './Comment_list';

const Comment_module = () => {
  const initial_data = [
    {author: "Luke", text: "Add comments to better explain how the code accomplishes its goal"},
    {author: "Simon", text: "Do something else that seems somehow a bit important"},
    {author: "Frank", text: "Change 3"},
    {author: "Hai", text: "Change 4"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"},
    {author: "Person", text: "Some Change"}
  ];

  const [comments, setComments] = useState(initial_data);

  return (
    <div>
      <p className="Comment-title">Comment Section</p>
      <div className="Comment-module-container">
        <Comment_list comments={comments} />
      </div>
    </div>
  );
};

export default Comment_module;