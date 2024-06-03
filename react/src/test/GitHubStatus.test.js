import React from "react";
import { render, waitFor } from "@testing-library/react";
import GitHubStatus from "../components/GitHub/GitHubStatus";
import { hasGitHubToken } from "../api/APIUtils";

jest.mock("../api/APIUtils", () => ({
  hasGitHubToken: jest.fn(),
}));

describe("GitHubStatus", () => {
  it("renders loading state initially", async () => {
    const props = {
      setConnected: jest.fn(),
      connected: false,
    };

    hasGitHubToken.mockResolvedValueOnce({ body: false });

    const { getByText } = render(<GitHubStatus {...props} />);

    expect(getByText("Loading...")).toBeInTheDocument();

    await waitFor(() => {
      expect(hasGitHubToken).toHaveBeenCalled();
      expect(props.setConnected).not.toHaveBeenCalled();
    });
  });

  it("renders connected state if hasGitHubToken returns true", async () => {
    const props = {
      setConnected: jest.fn(),
      connected: true,
    };

    const { getByText } = render(<GitHubStatus {...props} />);

    await waitFor(() => {
      expect(getByText("Connected to GitHub")).toBeInTheDocument();
    });
  });

  it("renders connect link if not connected to GitHub", async () => {
    const props = {
      setConnected: jest.fn(),
      connected: false,
    };

    hasGitHubToken.mockResolvedValueOnce({ body: false });

    const { getByText } = render(<GitHubStatus {...props} />);

    await waitFor(() => {
      expect(getByText("Connect to GitHub")).toBeInTheDocument();
      expect(props.setConnected).not.toHaveBeenCalled();
    });
  });
});