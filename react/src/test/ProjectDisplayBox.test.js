import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProjectDisplayBox from '../components/Projects/ProjectDisplayBox';
import { useNavigate } from 'react-router';
import { getAllProjectActiveCommentsForLatestCommit, getLatestCommitForProject } from '../api/APIUtils';
import { REVIEW_STATE } from '../utils/reviewStateMapping';
import { getColor } from '../utils/utils';

jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useNavigate: jest.fn(),
}));

jest.mock('../api/APIUtils', () => ({
  getAllProjectActiveCommentsForLatestCommit: jest.fn(),
  getLatestCommitForProject: jest.fn(),
}));

jest.mock('../utils/reviewStateMapping', () => ({
  REVIEW_STATE: {
    CLOSED: 'closed',
    OPEN: 'open',
  },
}));

jest.mock('../utils/utils', () => ({
  getColor: jest.fn(),
}));

describe('ProjectDisplayBox', () => {
  beforeEach(() => {
    useNavigate.mockReturnValue(jest.fn());
  });

  const mockProps = {
    id: 1,
    author: 'JohnDoe',
    name: 'MyProject',
    date: '2023-06-01',
  };

  it('should render correctly when loaded', async () => {
    getLatestCommitForProject.mockResolvedValue({ state: REVIEW_STATE.OPEN, approved_count: 3 });
    getAllProjectActiveCommentsForLatestCommit.mockResolvedValue([{ id: 1 }, { id: 2 }]);
    getColor.mockReturnValue('text-green-500');

    render(<ProjectDisplayBox {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('JohnDoe/MyProject')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2023-06-01')).toBeInTheDocument();
      expect(screen.getByText('OPEN')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  it('should navigate to the correct URL on click', async () => {
    getLatestCommitForProject.mockResolvedValue({ state: REVIEW_STATE.OPEN, approved_count: 0 });
    getAllProjectActiveCommentsForLatestCommit.mockResolvedValue([]);
    getColor.mockReturnValue('text-green-500');
    const mockNavigate = jest.fn();
    useNavigate.mockReturnValue(mockNavigate);

    render(<ProjectDisplayBox {...mockProps} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('JohnDoe/MyProject'));
      expect(mockNavigate).toHaveBeenCalledWith('/Project/1/Commit/0');
    });
  });

  it('should handle missing commit data gracefully', async () => {
    getLatestCommitForProject.mockResolvedValue(null);
    getAllProjectActiveCommentsForLatestCommit.mockResolvedValue([]);
    getColor.mockReturnValue('text-green-500');

    render(<ProjectDisplayBox {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('JohnDoe/MyProject')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2023-06-01')).toBeInTheDocument();
      expect(screen.getByText('CLOSED')).toBeInTheDocument();
    });
  });
});