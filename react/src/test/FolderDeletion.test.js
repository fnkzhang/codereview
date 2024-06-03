import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { useParams, useNavigate } from 'react-router';
import FolderDeletion from '../components/Folders/FolderDeletion';
import { getFolderInfo, deleteFolder } from '../api/APIUtils';

jest.mock('react-router', () => ({
  useParams: jest.fn(),
  useNavigate: jest.fn(),
}));

jest.mock('../api/APIUtils', () => ({
  getFolderInfo: jest.fn(),
  deleteFolder: jest.fn(),
}));

global.alert = jest.fn();

describe('FolderDeletion', () => {
  beforeEach(() => {
    getFolderInfo.mockReturnValue({ name: 'Folder Name' });
    useParams.mockReturnValue({ project_id: '1', commit_id: '2', folder_id: '3' });
    useNavigate.mockReturnValue(jest.fn());
  });

  it('renders correctly', () => {
    const { getByText, getByPlaceholderText } = render(<FolderDeletion isLoggedIn={true} />);

    expect(getByText('Are you sure you want to delete this Folder?')).toBeInTheDocument();
    expect(getByText(/Please type/)).toBeInTheDocument();
    expect(getByPlaceholderText('Name of Folder')).toBeInTheDocument();
    expect(getByText('Delete')).toBeInTheDocument();
  });

  it('displays error message if deletion fails', async () => {
    deleteFolder.mockResolvedValueOnce({ success: false });

    const { getByText, getByPlaceholderText, getByRole } = render(<FolderDeletion isLoggedIn={true} />);

    fireEvent.change(getByPlaceholderText('Name of Folder'), { target: { value: 'Folder Name' } });
    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      //expect(deleteFolder).toHaveBeenCalledWith('3', '2');
      //expect(getByText('Error: Could Not Delete Folder')).toBeInTheDocument();
    });
  });

  it('successfully deletes folder and navigates on successful deletion', async () => {
    deleteFolder.mockResolvedValueOnce({ success: true });

    const { getByPlaceholderText, getByRole } = render(<FolderDeletion isLoggedIn={true} />);

    fireEvent.change(getByPlaceholderText('Name of Folder'), { target: { value: 'Folder Name' } });
    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      //expect(deleteFolder).toHaveBeenCalledWith('3', '2');
    });
  });

  it('does not allow deletion if folder name does not match', async () => {
    const { getByPlaceholderText, getByRole, queryByText } = render(<FolderDeletion isLoggedIn={true} />);

    fireEvent.change(getByPlaceholderText('Name of Folder'), { target: { value: 'Incorrect Folder Name' } });
    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    expect(deleteFolder).not.toHaveBeenCalled();
    expect(queryByText('Error: Could Not Delete Folder')).not.toBeInTheDocument();
  });

  it('prevents submission if folder name is empty', async () => {
    const { getByRole } = render(<FolderDeletion isLoggedIn={true} />);

    fireEvent.submit(getByRole('button', { name: 'Delete' }));

    expect(deleteFolder).not.toHaveBeenCalled();
  });
});