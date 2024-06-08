import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import CommentModule from '../components/Comments/CommentModule';
import { createComment, getAllCommentsForDocument } from '../api/APIUtils';
import { useParams } from 'react-router';

// Mock API functions
jest.mock('../api/APIUtils', () => ({
  createComment: jest.fn(),
  getAllCommentsForDocument: jest.fn(),
}));

// Mock useParams
jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useParams: jest.fn(),
}));

describe('CommentModule', () => {
  const mockSetComments = jest.fn();
  const mockComments = [
    { author: 'John Doe', text: 'This is a comment.', snapshot_id: 1, is_resolved: false, date_modified: '2021-01-01T00:00:00Z' },
    { author: 'Jane Doe', text: 'This is another comment.', snapshot_id: 1, is_resolved: true, date_modified: '2021-01-02T00:00:00Z' },
  ];

  const mockUserData = {
    email: 'test@example.com',
  };

  beforeEach(() => {
    useParams.mockReturnValue({ document_id: '123' });
    getAllCommentsForDocument.mockResolvedValue(mockComments);
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    render(<CommentModule comments={[]} setComments={mockSetComments} />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('fetches and displays comments', async () => {
    render(<CommentModule comments={[]} setComments={mockSetComments} />);

    await waitFor(() => {
      expect(mockSetComments).toHaveBeenCalledWith(mockComments);
    });
  });


  it('handles new comment submission', async () => {
    createComment.mockResolvedValue({});

    await act(async () => {
      render(
        <CommentModule 
          snapshotId={0}
          comments={mockComments} 
          setComments={mockSetComments} 
          userData={mockUserData} 
          // Add necessary props for comment position
          start={{ column: 1, lineNumber: 1 }} 
          end={{ column: 5, lineNumber: 3 }}
        />
      );
    });

    const textarea = screen.getByRole('textbox');
    await act(async () => {
      fireEvent.change(textarea, { target: { value: 'New comment' } });
    });

    const button = screen.getByRole('button', { name: /Submit Comment/i });
    
    await act(async () => {
      fireEvent.click(button);
    });

    await waitFor(() => {
      expect(createComment).toHaveBeenCalledWith(
        0,
        'test@example.com',
        0,
        'New comment',
        1, // Example values for column
        1, // Example values for lineNumber
        5, // Example values for column
        3  // Example values for lineNumber
      );
    });

    expect(createComment).toHaveBeenCalledTimes(1);
    expect(textarea).toHaveValue('');
  });

  it('renders correctly after loading comments', async () => {
    render(<CommentModule comments={mockComments} setComments={mockSetComments} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
  });
});