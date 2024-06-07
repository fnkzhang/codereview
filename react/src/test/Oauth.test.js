import React from "react";
import { render, act, waitFor, screen } from "@testing-library/react";
import Oauth from "../components/Oauth.js";
import getCookie from "../utils/utils";
import { deleteCookie } from "../utils/utils";


// Import Google Login
jest.mock('@react-oauth/google', () => ({
  GoogleLogin: ({ onSuccess, onError }) => (
    <button onClick={() => onSuccess({ credential: 'mockCredential' })}>Mock Google Login</button>
  ),
}));


// Mocking Import
jest.mock('jwt-decode', () => () => ({
  email: "test@example.com",
  picture: "testPictureUrl"
}));

// Mocking Util function imports
jest.mock("../utils/utils", () => ( {
  __esModule: true, // This property makes it clear that we're mocking an ES6 module
  default: jest.fn(() => "HELLO"), // Mock the default export (getCookie)
  deleteCookie: jest.fn() // Mock the named export (deleteCookie)
}));


// Handles Fetch Call response




describe("Oauth component", () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () =>
        Promise.resolve({
          success: true,
          body: { email: "test@example.com", picture: "testPictureUrl" },
        }),
      })
    );
  });

  afterEach(() => {
    //jest.resetAllMocks();
  });

  it('should render the Google Login button when not logged in', async () => {
    render(
    <Oauth isLoggedIn={false} 
      setIsLoggedIn={jest.fn()} 
      userData={null} 
      setUserData={jest.fn()} 
      connected={false} 
      setConnected={jest.fn()} 
    />);

    expect(screen.getByText('Mock Google Login')).toBeInTheDocument();
  });


  it("Tries to get cookies if not logged in", async () => {

    await act( async() => {
      render(
        <Oauth 
        isLoggedIn={false}
        setIsLoggedIn={jest.fn()} 
        userData={null} 
        setUserData={jest.fn()} 
        connected={false} 
        setConnected={jest.fn()} 
        />        
      )
    });
    
    screen.debug()
    expect(getCookie).toHaveBeenCalledWith("cr_id_token");      
  });

  it("Tries to get fetch failed", async () => {
    
    global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () =>
        Promise.resolve({
          success: false
        }),
      })
    );
    console.log = jest.fn();
    
    await act( async() => {
      render(
        <Oauth 
        isLoggedIn={false}
        setIsLoggedIn={jest.fn()} 
        userData={null} 
        setUserData={jest.fn()} 
        connected={false} 
        setConnected={jest.fn()} 
        />        
      )
    });
    
    screen.debug()
    expect(getCookie).toHaveBeenCalledWith("cr_id_token");    
    expect(console.log).toHaveBeenCalledWith("Failed to validate token");  
  });

});
