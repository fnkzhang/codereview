import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { useLocation, useNavigate } from 'react-router-dom';
import UserHomePage from '../components/UserHomePage';
import { addGitHubToken } from '../api/APIUtils';

// Mock the dependencies
jest.mock('../api/APIUtils', () => ({
  addGitHubToken: jest.fn(),
}));

jest.mock('react-router-dom', () => ({
  useLocation: jest.fn(),
  useNavigate: jest.fn(),
}));

describe('UserHomePage', () => {
  const renderComponent = (props = {isLoggedIn: true}) => {
    render(
        <UserHomePage {...props} />
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useLocation.mockReturnValue({search: "something"})
    useNavigate.mockReturnValue(jest.fn())
  });

  it('should display loading message when code exists', () => {
    useLocation.mockReturnValueOnce({ search: '?code=githubCode' });
    renderComponent();

    expect(screen.getByText('Verifying connection...')).toBeInTheDocument();
  });
});