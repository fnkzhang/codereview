import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ProjectCreation from "../components/Projects/ProjectCreation";
import { useNavigate } from "react-router";
import { createProject, pullFromGitHub } from "../api/APIUtils";

// Mocking react-router
jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: jest.fn(),
}));

jest.mock("../api/APIUtils", () => ({
  createProject: jest.fn(),
  pullFromGitHub: jest.fn(),
}));

describe('ProjectCreation', () => {
    it('should render correctly when logged in', () => {
      const { getByText, getByPlaceholderText } = render(<ProjectCreation isLoggedIn={true} connected={false} setConnected={jest.fn()} />);
      expect(getByText('Create a New Project')).toBeInTheDocument();
      expect(getByText('Project Name')).toBeInTheDocument();
      expect(getByPlaceholderText('Name of Project')).toBeInTheDocument();
      expect(getByText('Create')).toBeInTheDocument();
    });

    it('should display error message if user is not logged in', () => {
      render(<ProjectCreation isLoggedIn={false} connected={false} setConnected={jest.fn()} />);
      expect(screen.getByText('You must Log in to view this page.')).toBeInTheDocument();
    });

    it('should call createProject function with correct parameters on form submission without GitHub import', async () => {
      useNavigate.mockReturnValue(jest.fn());
      createProject.mockReturnValue({ success: true });

      const { getByPlaceholderText, getByText } = render(<ProjectCreation isLoggedIn={true} connected={false} setConnected={jest.fn()} />);
      
      fireEvent.change(getByPlaceholderText('Name of Project'), { target: { value: 'New Project Name' } });
      fireEvent.click(getByText('Create'));

      await waitFor(() => {
        expect(createProject).toHaveBeenCalledWith('New Project Name');
      });
    });
});
