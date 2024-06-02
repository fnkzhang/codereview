import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SubCommentList from '../components/Comments/SubCommentList';

// Mock the SubComment component
jest.mock('../components/Comments/SubComment', () => {
  return function DummySubComment({ author, text }) {
    return (
      <div data-testid="subcomment">
        <strong>{author}</strong>
        <div>{text}</div>
      </div>
    );
  };
});

describe('SubCommentList', () => {
  it('renders a list of SubComment components', () => {
    const subcomments = [
      { author: 'John Doe', text: 'This is a comment.' },
      { author: 'Jane Doe', text: 'This is another comment.' }
    ];

    render(<SubCommentList subcomments={subcomments} />);

    const subcommentElements = screen.getAllByTestId('subcomment');
    expect(subcommentElements.length).toBe(2);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('This is a comment.')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('This is another comment.')).toBeInTheDocument();
  });

  it('renders nothing when subcomments is null', () => {
    const { container } = render(<SubCommentList subcomments={null} />);

    expect(container).toBeEmptyDOMElement();
  });
});