import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import MainWindow from '../components/MainWindow';
import '@testing-library/jest-dom/extend-expect';
import { createSnapshotForDocument } from '../api/APIUtils';

// Mock the dependencies
jest.mock('../components/ReviewWindow', () => {
  return (props) => <div data-testid="review-window">Mocked Review Window</div>;
});
jest.mock('../components/SnapshotSelector', () => {
  return (props) => <div data-testid="snapshot-selector">Mocked Snapshot Selector</div>;
});
jest.mock('../components/Buttons/BackButton', () => {
  return (props) => <button data-testid="back-button">Mocked Back Button</button>;
});
jest.mock('react-tooltip', () => ({
  Tooltip: (props) => <div data-testid="tooltip">{props.content}</div>
}));
jest.mock('../api/APIUtils', () => ({
  createSnapshotForDocument: jest.fn(),
}));

const mockNavigate = jest.fn();
jest.mock('react-router', () => ({
  useParams: () => ({
    project_id: '1',
    commit_id: '1',
    document_id: '1',
    left_snapshot_id: '1',
  }),
  useNavigate: () => mockNavigate,
  useLocation: () => ({
    state: {
      documentName: 'test.js',
      addSnapshots: true,
    },
  }),
}));

describe('MainWindow', () => {
  const renderComponent = (isLoggedIn) => {
    render(
        <MainWindow isLoggedIn={isLoggedIn} userData={{ name: 'testUser' }} />
    );
  };

  it('should display login prompt when user is not logged in', () => {
    renderComponent(false);
    expect(screen.getByText('You must Log in to view this page.')).toBeInTheDocument();
  });

  it('should display the main content when user is logged in', () => {
    renderComponent(true);
    expect(screen.getByTestId('back-button')).toBeInTheDocument();
    expect(screen.getByTestId('snapshot-selector')).toBeInTheDocument();
    expect(screen.getByTestId('review-window')).toBeInTheDocument();
  });
});
