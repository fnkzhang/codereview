import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ProjectExport from '../components/Projects/ProjectExport';
import '@testing-library/jest-dom/extend-expect';
import { getCommits, pushToExistingBranch } from '../api/APIUtils';

// Mock the dependencies
jest.mock('../components/Loading/LoadingSpinner', () => {
  return (props) => props.active ? <div data-testid="loading-spinner">Mocked Loading Spinner</div> : null;
});
jest.mock('../components//GitHub/GitHubStatus', () => {
  return (props) => <div data-testid="github-status">Mocked GitHub Status</div>;
});
jest.mock('../components//Commits/CommitDropdown', () => {
  return (props) => <div data-testid="commit-dropdown">Mocked Commit Dropdown</div>;
});
jest.mock('../api/APIUtils', () => ({
  getCommits: jest.fn(),
  pushToExistingBranch: jest.fn(),
}));

describe('ProjectExport', () => {
  const renderComponent = (isLoggedIn, connected) => {
    render(
      <MemoryRouter initialEntries={[`/project/1/export`]}>
        <Routes>
          <Route path="/project/:project_id/export" element={<ProjectExport isLoggedIn={isLoggedIn} connected={connected} setConnected={jest.fn()} />} />
        </Routes>
      </MemoryRouter>
    );
  };

  beforeEach(() => {
    getCommits.mockReturnValue({
        success: true,
        body: [
            { name: 'Commit 1', state: 'pending', commit_id: 1 },
            { name: 'Commit 2', state: 'prnding', commit_id: 2 }
        ]
    })
  });

  it('should display login prompt when user is not logged in', () => {
    renderComponent(false, true);
    expect(screen.getByText('You must Log in to view this page.')).toBeInTheDocument();
  });

  it('should display GitHub connection prompt when user is not connected to GitHub', () => {
    renderComponent(true, false);
    expect(screen.getByText('Connect to a GitHub account in order to export a project\'s contents.')).toBeInTheDocument();
    expect(screen.getByTestId('github-status')).toBeInTheDocument();
  });

  it('should display the form when user is logged in and connected to GitHub', async () => {
    getCommits.mockResolvedValue({ body: [{ commit_id: '123', date_committed: '2021-01-01' }] });
    renderComponent(true, true);

    await waitFor(() => expect(getCommits).toHaveBeenCalledTimes(1));

    expect(screen.getByLabelText('Repository Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Branch Name')).toBeInTheDocument();
    expect(screen.getByTestId('commit-dropdown')).toBeInTheDocument();
  });
});
