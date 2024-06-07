import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ProjectDeletion from "../components/Projects/ProjectDeletion";
import { useNavigate, useParams } from "react-router";
import { deleteProject, getProjectInfo } from "../api/APIUtils";

// Mocking react-router
jest.mock("react-router", () => ({
  ...jest.requireActual("react-router"),
  useNavigate: jest.fn(),
  useParams: jest.fn(),
}));

jest.mock("../api/APIUtils", () => ({
  deleteProject: jest.fn(),
  getProjectInfo: jest.fn(),
}));

describe('ProjectDeletion', () => {
    beforeEach(() => {
      useNavigate.mockReturnValue(jest.fn());
      useParams.mockReturnValue({ project_id: '123' });
    });

    it('should render correctly when logged in', async () => {
      getProjectInfo.mockResolvedValue({ name: 'Test Project' });
      
      render(<ProjectDeletion isLoggedIn={true} />);
      
      await waitFor(() => {
        expect(screen.getByText('Are you sure you want to delete this project?')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Name of Project')).toBeInTheDocument();
        expect(screen.getByText('Delete')).toBeInTheDocument();
      });
    });

    it('should display error message if user is not logged in', () => {
      render(<ProjectDeletion isLoggedIn={false} />);
      expect(screen.getByText('You must Log in to view this page.')).toBeInTheDocument();
    });

    it('should alert if the input project name does not match the actual project name', async () => {
      getProjectInfo.mockResolvedValue({ name: 'Test Project' });
      window.alert = jest.fn();
      
      render(<ProjectDeletion isLoggedIn={true} />);
      
      await waitFor(() => {
        fireEvent.change(screen.getByPlaceholderText('Name of Project'), { target: { value: 'Wrong Project Name' } });
        fireEvent.click(screen.getByText('Delete'));
      });
      
      expect(window.alert).toHaveBeenCalledWith("Input Does Not Match Project Name");
    });
});