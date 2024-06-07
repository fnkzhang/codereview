import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react";
import Oauth from "../components/Oauth.js";
import getCookie from "../utils/utils.js";
import { deleteCookie } from "../utils/utils.js";

import {GoogleOAuthProvider} from '@react-oauth/google';


jest.mock("@react-oauth/google", () => {
  return {
    GoogleOAuthProvider: jest.fn(({children}) => <div>{children}</div>)
  }
})

jest.mock('../utils/utils', () => ({
  getCookie: jest.fn(() => 'testToken'), // Mock the getCookie function
  deleteCookie: jest.fn(),
}));

const MockGoogleOAuthProvider = ({ children }) => {
  return (
    <GoogleOAuthProvider clientId="">
      {children}
    </GoogleOAuthProvider>
  );
};

describe("Oauth component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders without crashing", () => {
    render(
      <MockGoogleOAuthProvider>
        <Oauth />
      </MockGoogleOAuthProvider>
    );
  });

  it("Tries to get cookies if not logged in", () => {
    const isLoggedIn = false;

    render(
      <MockGoogleOAuthProvider>
        <Oauth isLoggedIn={isLoggedIn}/>
      </MockGoogleOAuthProvider>
    );

    waitFor(() => {
      expect(getCookie).hasBeenCalled();
    })
  });

});
