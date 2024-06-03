import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import DocumentCreation from '../components/Documents/DocumentCreation';
import { useParams, useNavigate } from 'react-router';
import { createDocument } from '../api/APIUtils';

// Mocking react-router
jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useParams: jest.fn(),
  useNavigate: jest.fn(),
}));

// Mocking FileInput component
jest.mock('flowbite-react', () => ({
  ...jest.requireActual('flowbite-react'),
  FileInput: jest.fn(({ onChange }) => (
    <input type="file" data-testid="file-input" onChange={onChange} />
  )),
}));

// Mocking APIUtils
jest.mock('../api/APIUtils', () => ({
  createDocument: jest.fn(),
}));

describe('DocumentCreation', () => {
  it('should render correctly', () => {
    useParams.mockReturnValue({ project_id: '123', commit_id: '456', parent_folder_id: '789' });
    const { getByText } = render(<DocumentCreation isLoggedIn={true} />);
    expect(getByText('New Document')).toBeInTheDocument();
    expect(getByText('Upload Document')).toBeInTheDocument();
  });

  it('should display error message if user is not logged in', async () => {
    useParams.mockReturnValue({ project_id: '123', commit_id: '456', parent_folder_id: '789' });
    const { getByText } = render(<DocumentCreation isLoggedIn={false} />);
    expect(getByText('You must Log in to view this page.')).toBeInTheDocument();
  });
});