# Code Review UI

## Description
This react project provides an intuitive way to interact with, and uitlize the functionality implemented by the Flask Backend.

With it, users can import code repositories from GitHub, add and modify files as necessary throughout the code review, and finally export the modified project back to GitHub.

## Features
- Google Oauth Authentication
- GitHub Account Connection and Integration
- Code Review Creation
- Code Review Collaberation
- Code Review State Management
- Code Review Exporting

## Screenshots
![Home Page](../screenshots/homepage.png)
![Project Page](../screenshots/commitpage.png)
![Edit Page](../screenshots/editpage.png)
![Export Page](../screenshots/exportpage.png)

## Technologies Used
- React
- React Router
- Tailwind CSS
- Flowbite Component Library
- Jest

## Project Structure
codereview/react/<br>
├── nginx/ # Nginx Config Files<br>
├── public/ # Static Files<br>
├── src/ # Source Files<br>
│   ├── api/ # API Service Files<br>
│   ├── components/ # Application Components<br>
│   ├── test/ # Jest Test Files<br>
│   ├── utils/ # Utility Files<br>
│   ├── App.js # Main App Compnent<br>
│   ├── index.css # Index.html Styling Config<br>
│   ├── index.js # Google Oauth Setup<br>
├── tailwind.config.json<br>
└── package.json<br>

## Running The UI

To ensure that the package build tree is valid, and the packages are correctly installed, use the following command:

    npm install

Before attempting to run the UI in development mode, it is recommended that the Test scripts are run. To run the provided unit tests use the following command:

    npm test

To run the UI in developer mode use the following command:

    npm start

When deploying this project it is recommended not to build the UI natively, and instead utilize docker so it can be more easily supplied to a Google Cloud Run service. For more detailed deployment information, see the [deployment instructions](../README.md).

