import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import CommitDropdown from '../components/Commits/CommitDropdown';

describe('CommitDropdown', () => {
  const commits = [
    { name: 'Commit 1', state: 'pending' },
    { name: 'Commit 2', state: 'success' },
    { name: 'Commit 3', state: 'failure' },
  ];

  it('renders correctly', () => {
    const { getByText } = render(<CommitDropdown commits={commits} commit={commits[0]}/>);

    expect(getByText('Commit 1')).toBeInTheDocument();
  });

  it('calls setCommit and setCommitLoading when a commit is clicked', () => {
    const setCommit = jest.fn();
    const setCommitLoading = jest.fn();

    const { getByText } = render(
      <CommitDropdown commits={commits} commit={commits[0]} setCommit={setCommit} setCommitLoading={setCommitLoading} />
    );

    fireEvent.click(getByText('Commit 1'));
    fireEvent.click(getByText('Commit 2'));

    expect(setCommit).toHaveBeenCalledWith(commits[1]);
    expect(setCommitLoading).toHaveBeenCalledWith(true);
  });
});