import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import '@testing-library/jest-dom/extend-expect';
import ProjectPage from "../components/ProjectPage";
import { useNavigate, useParams } from "react-router";
import { getAllSnapshotsFromDocument, getAllUsersWithPermissionForProject, getProjectInfo, getFolderTree,
    getCommits, createCommit, approveCommit, setCommitReviewed, 
    getLatestCommitForProject, setCommitClosed } from "../api/APIUtils";

// Mocking APIUtils
jest.mock("../api/APIUtils", () => ({
    getAllSnapshotsFromDocument: jest.fn(), 
    getAllUsersWithPermissionForProject: jest.fn(), 
    getProjectInfo: jest.fn(),
    getFolderTree: jest.fn(),
    getCommits: jest.fn(),
    createCommit: jest.fn(),
    approveCommit: jest.fn(),
    setCommitReviewed: jest.fn(), 
    getLatestCommitForProject: jest.fn(), 
    setCommitClosed: jest.fn()
}));

// Mocking react-router useParams
jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: jest.fn(),
  useParams: jest.fn(),
}));

describe('ProjectPage', () => {
  const mockParams = {
    project_id: "1",
    commit_id: "2"
  };

  const mockNavigate = jest.fn()
  const testEmail = "test@example.com"
  const commit = { name: 'Commit 1', state: 'open' }
  const projectInfo = {
    proj_id: 1,
    name: 'Project Name',
    author_email: testEmail,
    date_modified: '2023-06-01T12:34:56Z',
  }

  beforeEach(() => {
    useParams.mockReturnValue(mockParams);
    useNavigate.mockReturnValue(mockNavigate)
    getAllUsersWithPermissionForProject.mockReturnValue([{email : testEmail}])
    getLatestCommitForProject.mockReturnValue(commit)
    getProjectInfo.mockReturnValue(projectInfo)
    getFolderTree.mockReturnValue({content:{documents: [], folders: []}})
    getCommits.mockReturnValue([commit])
  });

  it('should render loading state initially', () => {
    render(<ProjectPage isLoggedIn={true} userData={{email : testEmail}}/>);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  // Add more test cases as needed...
});