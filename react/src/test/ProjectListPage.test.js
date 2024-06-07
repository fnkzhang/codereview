import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import '@testing-library/jest-dom/extend-expect';
import ProjectListPage from "../components/Projects/ProjectListPage";
import { getUserProjects } from "../api/APIUtils";
import { useNavigate } from "react-router";

// Mocking react-router
jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: jest.fn(),
}));

// Mocking APIUtils
jest.mock("../api/APIUtils", () => ({
  getUserProjects: jest.fn(),
}));

describe('ProjectListPage', () => {
  const mockNavigate = jest.fn();
  const mockUserProjects = [
    {
      proj_id: 1,
      name: 'Project 1',
      author_email: 'user1@example.com',
      date_modified: '2023-06-01T12:34:56Z',
    },
    {
      proj_id: 2,
      name: 'Project 2',
      author_email: 'user2@example.com',
      date_modified: '2023-06-02T12:34:56Z',
    },
  ];

  beforeEach(() => {
    useNavigate.mockReturnValue(mockNavigate);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should render loading state initially', () => {
    render(<ProjectListPage isLoggedIn={true} userData={{ email: 'user@example.com' }} />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should render project list when logged in and projects are available', async () => {
    getUserProjects.mockResolvedValue(mockUserProjects);

    render(<ProjectListPage isLoggedIn={true} userData={{ email: 'user@example.com' }} />);

    await waitFor(() => expect(getUserProjects).toHaveBeenCalledWith('user@example.com'));
  });

  it('should render no projects available message when logged in but no projects are available', async () => {
    getUserProjects.mockResolvedValue([]);

    render(<ProjectListPage isLoggedIn={true} userData={{ email: 'user@example.com' }} />);

    await waitFor(() => expect(getUserProjects).toHaveBeenCalledWith('user@example.com'));

    await waitFor(() => {
      expect(screen.getByText('No projects Available.')).toBeInTheDocument();
    });
  });

  it('should navigate to create project page when create project button is clicked', () => {
    render(<ProjectListPage isLoggedIn={true} userData={{ email: 'user@example.com' }} />);
    fireEvent.click(screen.getByText('Create Project'));
    expect(mockNavigate).toHaveBeenCalledWith('/Project/Create');
  });
});