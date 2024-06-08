import React from "react";
import { render, fireEvent } from "@testing-library/react";
import GitHubImportForm from "../components/GitHub/GitHubImportForm";

describe("GitHubImportForm", () => {
  it("renders correctly when not connected to GitHub", () => {
    const props = {
      connected: false,
      setConnected: jest.fn(),
      importFromGitHub: false,
      setImportFromGitHub: jest.fn(),
      setGitRepo: jest.fn(),
      setRepoBranch: jest.fn(),
    };

    const { getByText } = render(<GitHubImportForm {...props} />);

    expect(
      getByText(
        "Connect to a GitHub account in order to import a project's contents."
      )
    ).toBeInTheDocument();
  });

  it("renders correctly when connected to GitHub but not importing", () => {
    const props = {
      connected: true,
      setConnected: jest.fn(),
      importFromGitHub: false,
      setImportFromGitHub: jest.fn(),
      setGitRepo: jest.fn(),
      setRepoBranch: jest.fn(),
    };

    const { getByText, getByLabelText } = render(
      <GitHubImportForm {...props} />
    );

    expect(getByLabelText("Import project contents from GitHub.")).toBeInTheDocument();
  });

  it("renders correctly when connected to GitHub and importing", () => {
    const props = {
      connected: true,
      setConnected: jest.fn(),
      importFromGitHub: true,
      setImportFromGitHub: jest.fn(),
      setGitRepo: jest.fn(),
      setRepoBranch: jest.fn(),
    };

    const { getByText, getByLabelText, getByPlaceholderText } = render(
      <GitHubImportForm {...props} />
    );

    expect(getByLabelText("Import project contents from GitHub.")).toBeInTheDocument();
    expect(getByPlaceholderText("Name of GitHub Repository")).toBeInTheDocument();
    expect(getByPlaceholderText("Name of Branch")).toBeInTheDocument();
  });

  it("triggers correct function when import checkbox is clicked", () => {
    const props = {
      connected: true,
      setConnected: jest.fn(),
      importFromGitHub: false,
      setImportFromGitHub: jest.fn(),
      setGitRepo: jest.fn(),
      setRepoBranch: jest.fn(),
    };

    const { getByLabelText } = render(<GitHubImportForm {...props} />);
    const importCheckbox = getByLabelText("Import project contents from GitHub.");

    fireEvent.click(importCheckbox);

    expect(props.setImportFromGitHub).toHaveBeenCalledWith(true);
  });

  it("triggers correct function when repository name input is changed", () => {
    const props = {
      connected: true,
      setConnected: jest.fn(),
      importFromGitHub: true,
      setImportFromGitHub: jest.fn(),
      setGitRepo: jest.fn(),
      setRepoBranch: jest.fn(),
    };

    const { getByPlaceholderText } = render(<GitHubImportForm {...props} />);
    const repoNameInput = getByPlaceholderText("Name of GitHub Repository");

    fireEvent.change(repoNameInput, { target: { value: "my-repo" } });

    expect(props.setGitRepo).toHaveBeenCalledWith("my-repo");
  });

  it("triggers correct function when branch name input is changed", () => {
    const props = {
      connected: true,
      setConnected: jest.fn(),
      importFromGitHub: true,
      setImportFromGitHub: jest.fn(),
      setGitRepo: jest.fn(),
      setRepoBranch: jest.fn(),
    };

    const { getByPlaceholderText } = render(<GitHubImportForm {...props} />);
    const branchNameInput = getByPlaceholderText("Name of Branch");

    fireEvent.change(branchNameInput, { target: { value: "main" } });

    expect(props.setRepoBranch).toHaveBeenCalledWith("main");
  });
});