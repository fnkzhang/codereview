import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import CommitSubmission from '../components/Commits/CommitSubmission';
import { useParams, useNavigate } from 'react-router';
import { submitCommit } from '../api/APIUtils';

// Mocking react-router
jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useParams: jest.fn(),
  useNavigate: jest.fn(),
}));

// Mocking APIUtils
jest.mock('../api/APIUtils', () => ({
    submitCommit: jest.fn(),
  }));

describe('CommitSubmission', () => {
  it('should render correctly', () => {
    useParams.mockReturnValue({ project_id: '123', commit_id: '456' });
    useNavigate.mockReturnValue(jest.fn());
    const { getByText, getByPlaceholderText } = render(<CommitSubmission isLoggedIn={true} />);
    expect(getByText('Commit Your Working Changes')).toBeInTheDocument();
    expect(getByPlaceholderText('Name of Commit')).toBeInTheDocument();
  });

  it('should display error message if commit name is empty', async () => {
    useParams.mockReturnValue({ project_id: '123', commit_id: '456' });
    useNavigate.mockReturnValue(jest.fn());
    const { getByText } = render(<CommitSubmission isLoggedIn={true} />);
    fireEvent.click(getByText('Commit'));
    await waitFor(() => expect(getByText('Please provide a name for your commit.')).toBeInTheDocument());
  });

  it('should submit form and navigate on successful commit', async () => {
    useParams.mockReturnValue({ project_id: '123', commit_id: '456' });
    useNavigate.mockReturnValue(jest.fn());
    submitCommit.mockReturnValue({ success: true });
    const { getByText, getByPlaceholderText } = render(<CommitSubmission isLoggedIn={true} />);
    fireEvent.change(getByPlaceholderText('Name of Commit'), { target: { value: 'My Commit' } });
    fireEvent.click(getByText('Commit'));
    expect(require('../api/APIUtils').submitCommit).toHaveBeenCalledWith('456', 'My Commit');
  });
});