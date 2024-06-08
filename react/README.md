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

To understand what pages contain what components, begin with the App.js file. This file is the root component of the application, and manages the state of the user, and their GitHub connection status.

Additionally, explanations of how the components operate and what they intend to do can be found in each source file in JSDoc notation.

## Running The React Project

To ensure that the package build tree is valid, and the packages are correctly installed, use the following command:

    npm install

Before attempting to run the UI in development mode, it is recommended that the Test scripts are run. To run the provided unit tests use the following command:

    npm test

To run the UI in developer mode use the following command:

    npm start

When deploying this project it is recommended not to build the UI natively, and instead utilize docker so it can be more easily supplied to a Google Cloud Run service. For more detailed deployment information, see the [deployment instructions](../README.md).


## Using The Application

The applicaiton from the UI perspective generally follows the below steps:

1. Code Review "Project" is created by code author
2. The author shares the review "Project" with a reviewer
3. The reviewer leaves comments as necessary
4. The author implmenet the necessary changes and commits them
5. The reviewer and suthor continue steps 3 and 4 until the reviewer is content with the changes
6. The author exports the project back to GitHub

For more detailed instructions on how to use the application, continue reading below.

### Signing Up

To sign up for the application, all that is needed is the user to log in with their google account. This will automatically add them internally to the application, so they can then use most of the other available services.

In order for the user to access GitHub services, they will need to connect to their GitHub account. The user will not be able to import code from GitHub, or export their code back to GitHub without connecting their account to GitHub. To connect the account, the user must click on the dropdown in the top right, and then select the option "Connect to GitHub". The user should be redirected to GitHub, and upon logging in they will be redirected back to the home page of the Code Review application.

### Creating a Project

A single code review instance is contained within a project. From the application's Home Page, the user can create a project, where they may choose to create a blank project or import a project from GitHub.

Once a project has been created it will have a review-state (starts in the "open" state) which will be visible. By clicking on the Project a user should be able to see its contents.

### Sharing a Project

Within a project, the owner of the project is considered to be the code "author", and the individuals which the project is shared with are the code "reviewer".

The owner can allow multiple users to have access to the project by clicking on the share button while viewing a project. This will take them to the project page where they may choose to add new users to the project (usually a reviewer) or remove access from users. The owner can also Tranfer ownership, but only one user can be the owner of a project.

### Reviewing a project

When a reviewer is reviewing a project they can click on the dropdown associated with a document and view it. This will direct them to a page where they can leave comments on the document and then when they return to the project-view they can choose either to mark the changes as "Approved" or "Needs Changes".

When other users return to the project, they should be greeted with a notification that their are new comments, and it should be clear that the project's state has changed.

### Implementing the Changes

The application uses a notion of bundling changes in order to allow the author to make multiple changes before notifying the reviewer. The location where these changes are stored, before being committed, is called the users "Working Commit". In this location the user can create new files, delete new files, and modify existing files. To modify an existing file the user needs to view it, change the code in the right side of the editor, and then click the button that says "Add New Snapshot". If the user does not have a working commit, one will be created, and the new snapshot will be treated as the active version of the file in the working commit. T

When the user is ready to commit their changes, from the project view click the button labeled "Commit Changes". Once this is done, the state of the project will return to "Open" and the reviewer can go back to reviewing the code in the new Commit.

### Changing Project State

The review state can change implicitly and explicitly. The review starts in the "Open" state and can only leave that state when the reviewer states that the code offered by the author is "Approved" or if it "Needs Changes". There are buttons available to the reviewer to select these options from the "Project" view.

When a commit has been approved by the reviewer, the state will move to "Approved" and when the author returns to the project, it will indivate that the review can be closed. Once the author clicks the "Close Review" Button the project state will be moved to closed an the review is complete.

### Exporting the Project

Once the review is completed, any user (but usually the Owner/Author) can select the "Export Project" button. If the user is connected to GitHub they can specify the repository and branch thaty needs to be exported to and then all of the changes that were accrued over the course of the review can be sent back to GitHub.

From the Commit in GitHub it should be possible to see what comments were left unresolved by the reviewer on the files within the review, and should indicate that the changes were commited as part of the Code Review Web App.
