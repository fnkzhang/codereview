import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { DiffEditor } from '@monaco-editor/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ReviewWindow from '../components/ReviewWindow';
import '@testing-library/jest-dom/extend-expect';
import { getDocSnapshot, getCommitData } from '../api/APIUtils';

// Mock the dependencies
jest.mock('@monaco-editor/react', () => ({
  DiffEditor: jest.fn(() => <div data-testid="diff-editor">Mocked DiffEditor</div>),
}));
jest.mock('../components/Comments/CommentModule', () => {
  return (props) => <div data-testid="comment-module">Mocked CommentModule</div>;
});
jest.mock('../api/APIUtils', () => ({
  getDocSnapshot: jest.fn(),
  getCommitData: jest.fn(),
}));

jest.mock('react-router', () => ({
  useParams: () => ({
    project_id: '1',
    commit_id: '1',
    document_id: '1',
    left_snapshot_id: '1',
    right_snapshot_id: '1',
  }),
  useLocation: () => ({
    state: {
      documentName: 'test.js',
      addSnapshots: true,
    },
  }),
}));

describe('ReviewWindow', () => {
  const renderComponent = (props = {}) => {
    const defaultProps = {
      comments: [],
      setComments: jest.fn(),
      userData: { name: 'testUser' },
      hasUpdatedCode: false,
      setHasUpdatedCode: jest.fn(),
      setDataToUpload: jest.fn(),
      editorReady: false,
      setEditorReady: jest.fn(),
      editorLanguage: 'javascript',
      ...props,
    };

    render(
        <ReviewWindow {...defaultProps} />
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should display loading state initially', () => {
    getDocSnapshot.mockResolvedValue({ body: 'code' });
    renderComponent();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

});