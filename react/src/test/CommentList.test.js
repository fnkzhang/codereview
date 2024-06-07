import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import CommentList from '../components/Comments/CommentList';

// Correct the path if necessary
jest.mock('../components/Comments/Comments', () => () => <div>Mocked Comment</div>);

describe('CommentList', () => {
  it('renders null if comments is not an array', () => {
    const { container } = render(<CommentList comments={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders a list of comments when provided with a valid comments array', () => {
    const comments = [
      {
        comment_id: '1',
        author_email: 'author1@example.com',
        content: 'Comment 1',
        subcomments: [],
        date_modified: '2023-05-01T12:00:00Z',
        snapshot_id: 'snap1',
        highlight_start_x: 1,
        highlight_start_y: 1,
        highlight_end_x: 2,
        highlight_end_y: 2,
        is_resolved: false,
      },
      {
        comment_id: '2',
        author_email: 'author2@example.com',
        content: 'Comment 2',
        subcomments: [],
        date_modified: '2023-05-02T12:00:00Z',
        snapshot_id: 'snap2',
        highlight_start_x: 1,
        highlight_start_y: 1,
        highlight_end_x: 2,
        highlight_end_y: 2,
        is_resolved: true,
      },
    ];

    const { getAllByText } = render(
      <CommentList 
        setCommentsLoading={jest.fn()} 
        comments={comments} 
        listLineJump={jest.fn()} 
        editorLanguage="javascript" 
        editorCode="console.log('Hello World');" 
        checkIfCanGetLLMCode={jest.fn()} 
        getHighlightedCode={jest.fn()} 
        updateHighlightedCode={jest.fn()} 
        commitState={{}} 
        userData={{}}
      />
    );

    expect(getAllByText('Mocked Comment')).toHaveLength(2);
  });
});