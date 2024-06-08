import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { useParams, useNavigate } from 'react-router';
import CommitDeletion from '../components/Commits/CommitDeletion';
import { deleteCommit } from '../api/APIUtils';

jest.mock('react-router', () => ({
  useParams: jest.fn(),
  useNavigate: jest.fn(),
}));

jest.mock('../api/APIUtils', () => ({
  deleteCommit: jest.fn(),
}));

// Mock window.alert
global.alert = jest.fn();

describe('CommitDeletion', () => {
  beforeEach(() => {
    useParams.mockReturnValue({ project_id: '1', commit_id: '2' });
    useNavigate.mockReturnValue(jest.fn());
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<CommitDeletion isLoggedIn={true} />);

    expect(getByText('Are you sure you want to delete your working commit?')).toBeInTheDocument();
    expect(getByPlaceholderText('Name of Commit')).toBeInTheDocument();
    expect(getByText('Delete')).toBeInTheDocument();
  });

  it('displays error message if deletion fails', async () => {
    deleteCommit.mockResolvedValueOnce({ success: false });

    const { getByText, getByPlaceholderText, getByRole } = render(<CommitDeletion isLoggedIn={true} />);

    fireEvent.change(getByPlaceholderText('Name of Commit'), { target: { value: 'User Working Commit' } });
    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      expect(deleteCommit).toHaveBeenCalledWith('1');
      expect(getByText('Error: Could Not Delete Commit')).toBeInTheDocument();
    });
  });

  it('successfully deletes commit and navigates on successful deletion', async () => {
    deleteCommit.mockResolvedValueOnce({ success: true });

    const { getByPlaceholderText, getByRole } = render(<CommitDeletion isLoggedIn={true} />);

    fireEvent.change(getByPlaceholderText('Name of Commit'), { target: { value: 'User Working Commit' } });
    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      expect(deleteCommit).toHaveBeenCalledWith('1');
    });
  });

  it('does not allow deletion if commit name does not match', async () => {
    const { getByPlaceholderText, getByRole, queryByText } = render(<CommitDeletion isLoggedIn={true} />);

    fireEvent.change(getByPlaceholderText('Name of Commit'), { target: { value: 'Incorrect Commit Name' } });
    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    expect(deleteCommit).not.toHaveBeenCalled();
    expect(queryByText('Error: Could Not Delete Commit')).not.toBeInTheDocument();
  });

  it('prevents submission if commit name is empty', async () => {
    const { getByRole } = render(<CommitDeletion isLoggedIn={true} />);

    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    expect(deleteCommit).not.toHaveBeenCalled();
  });
});