import React from "react";
import { render } from "@testing-library/react";
import LoadingSpinner from "../components/Loading/LoadingSpinner";

describe("LoadingSpinner", () => {
  it("renders when active prop is true", () => {
    const { container } = render(<LoadingSpinner active={true} />);
    const spinnerSvg = container.querySelector("svg");
    expect(spinnerSvg).toBeInTheDocument();
  });

  it("does not render when active prop is false", () => {
    const { container } = render(<LoadingSpinner active={false} />);
    const spinnerSvg = container.querySelector("svg");
    expect(spinnerSvg).not.toBeInTheDocument();
  });
});