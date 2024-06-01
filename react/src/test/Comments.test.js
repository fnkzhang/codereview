// src/components/Comment.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import Comment from '../components/Comments/Comments';
import { resolveComment } from '../api/APIUtils';
import userEvent from '@testing-library/user-event';

// Mock the resolveComment function
jest.mock('../api/APIUtils', () => ({
  resolveComment: jest.fn(),
}));

// Mock the LlmButton and LoadingSpinner components
jest.mock('../components/LLM/LlmButton', () => () => <div>LlmButton Mock</div>);
jest.mock('../components/Loading/LoadingSpinner', () => () => <div>Loading...</div>);

describe('Comment Component', () => {
  const defaultProps = {
    setCommentsLoading: jest.fn(),
    commentID: '1',
    author: 'test@example.com',
    text: 'This is a comment',
    subcomments: [],
    date: '2023-05-30',
    commentLineJump: jest.fn(),
    snapshotID: 'snapshot1',
    highlightStartX: 0,
    highlightStartY: 0,
    highlightEndX: 100,
    highlightEndY: 100,
    isResolved: false,
    editorLanguage: 'javascript',
    editorCode: 'console.log("Hello World");',
    checkIfCanGetLLMCode: jest.fn().mockReturnValue(true),
    getHighlightedCode: jest.fn(),
    updateHighlightedCode: jest.fn(),
    commitState: {},
    userData: { email: 'test@example.com' },
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading spinner when userData is undefined', () => {
    render(<Comment {...defaultProps} userData={undefined} />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('renders the comment and buttons when data is loaded', () => {
    render(<Comment {...defaultProps} />);
    expect(screen.getByText('This is a comment')).toBeInTheDocument();
    expect(screen.getByText('Jump to Line')).toBeInTheDocument();
    expect(screen.getByText('Resolve Comment')).toBeInTheDocument();
  });

  test('calls resolveComment when the resolve button is clicked', async () => {
    resolveComment.mockResolvedValue('Resolved');

    render(<Comment {...defaultProps} />);

    userEvent.click(screen.getByText('Resolve Comment'));

    await waitFor(() => expect(resolveComment).toHaveBeenCalledWith('1'));
  });

  test('does not show resolve button if user is not the author', () => {
    const nonAuthorProps = { ...defaultProps, userData: { email: 'another@example.com' } };
    render(<Comment {...nonAuthorProps} />);
    expect(screen.queryByText('Resolve Comment')).not.toBeInTheDocument();
  });

  test('calls commentLineJump when the jump button is clicked', () => {
    render(<Comment {...defaultProps} />);
    userEvent.click(screen.getByText('Jump to Line'));
    expect(defaultProps.commentLineJump).toHaveBeenCalledWith(
      'snapshot1', 0, 0, 100, 100
    );
  });
});