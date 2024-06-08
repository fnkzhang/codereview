## Code Review Website
    A web site that can manage code reviews. To allow for ease of use, it shows a diff view for two versions of a file,

    and allows for comments on highlighted sections of text. Reviewers can propose their own changes that the original 

    author can either accept or reject on top of making comment suggestions.

## How To Use Project

### User Sign Up
    Loading in the main dashboard/homepage, if you are not logged in, the website will tell you that you must log in. 

    On the right side of the navigation bar, there will be a Google Login button that when pressed will open up a popup where you will login to your Google Account. Once logged in, your account will be created.

### Github Import
    Once you have logged in, it is recommended to link your Github account to the project for the best experience.

    Located on the right side of the navbar, there you will see a dropdown that when clicked, display logout, and connect to Github.
    Clicking on the connect to Github button will redirect you to Github, where you will log.

    Once logged in, you will have Github connected to your account.

### Start a Review
    Now for the main feature of the app, to start a review, direct yourself to the dashboard/homepage. From there, you will see a button called Create Project.

    Clicking on the button redirect you to a page for project creation which will be a simple name.
    Preferably, you will want to import your code from Github and to do so, you will click the checkbox which will then prompt you to enter your github repository name, and the branch you want to create a review for.

    The github repository should be in the format of:

        <Github Username>/<Repository Name>
    
    The branch name should match the branch you want to start a review for.


    After clicking create, it will take some time as it creates the project from the review.
    Once the project creation is done, you will be redirected back to home where a new project is now displayed. You have an Open Review.

### Sharing Reviewers

    You will want to have reviewers take a look at your code so first, click on the review, and then after loading, click on the **Share** button.

    From there you can manage, the users who have access to the project or you can enter the reviewer's email to give them access to the review.

### What To Do As A Reviewer

    As a reviewer, what will you do?

    First, locate an open project which signals that the author is waiting for someone to review it.

    Entering the review, view the files that the author has submitted, and provide your critiques and suggestions through comments.

    Above each editor, there is a dropdown that displays previous versions of the review. You can access the prior version of the review to see what the author has changed based on the suggestions that reviewers have provided.

    Once you have finished looking over all the code, in the review page, there will be 2 buttons on the top right which are **Approve** and **Needs Changes**.

#### What To Do When Code Needs Changes?
    
    Click on the **Needs Changes** button which will redirect you back to home and mark the review as **Reviewed**.

    From there, the author will make their adjustments.

#### What To Do When You Are Happy With The Code?

    If you think the changes are good click on the **Approve** button which will mark the review as Approved and redirect you back to home.

    From there, you the author will close the review, and push their changes to the Github repo.

### What To Do As An Author

    After posting a review and sharing it to a reviewer, you will wait until your review has been set to **Reviewed**.

    In the review page, you can see inside of each review how many suggestions have been made from the number in the yellow/orange box. If there are no suggestions, the box will not be visible.

    You can also see how many reviewers have approved of your code from the number in the green box. If there are no approvals, the box will not be visible.

#### What To Do When Review Is In Reviewed State

    If a reviewer has made suggestions you will see the number of suggestions under the review.

    Enter the review and locate the files that have new comments in them.

    From there you will use the suggestions to adjust your code.

    **Import**
        You can **Edit** the **Right Editor** while the **Left Editor** is **View Only**.
    
    After finishing your adjustment for a file, above the comments section, there will be a button that says **Create New Snapshot**.
    Clicking on the button will stage your changes but **Not** publish.

    After you are done adjusting your code, the review page will have a button called **Commit Changes** which once clicked will prompt you to enter a title for the commit.

    Similar to a Git Commit, you will write a descriptive name for the commit before pushing it.

    Now your review is set to open and the review process starts again.

#### What To Do When Review is Approved State

    If your reviewers are happy with your changes, your review will be labeled with green text: Approved.

    Entering your review, you can now locate the green button labeled **Close Review** which when clicked will now officially close the review.

    From there you can locate the Export Project Button to export the project.

    If there are still some additional suggestions, you can still make adjustments to restart the review or make adjustments and export the project.

    Any existing comments in the review will be sent along with the changes when exporting.

### Comments

    In each document, there will be comments that can be written by anyone with access to the review.

    Under each comment there can exist 3 buttons: Resolve Comment, Jump to Line, and Create LLM Suggestion.

    Resolve Comment can only be visible by the author of the comment and sets the suggestion as resolved.
    Jump to Line is visible for everyone and when clicked, will highlight the code in the editor that the comment pertains to.
    Create LLM Suggestion is only visible for the author of the code review and when clicked, an AI will automatically try to implement changes to the code based on the comment.

    **Important**
        Create LLM Suggestion is only visible when both editors are displaying the latest version of the code.

#### Creating Comments

    To create a comment, simply enter your text into the input field at the bottom of the comment section.

    It is **preferred** that you also highlight in the editor the section of code that your comment pertains to.

### How To Export Project To Github

    Once you are ready to push your changes to Github, as the author, enter the review and click on the **Export Project** button.

    You will be redirected and prompted to enter the repository name and branch you are trying to push to, similar to how you created the review.

    You can select which commit version you want push under the commit dropdown.

    Once you are ready, clicking on export will push all your changes into the Github repository branch.
    **Note** It will take some time to finish exporting, the page will redirect you back home after it is done exporting.

## Initialization For Development

### React
    With Node.js installed, move to the react directory folder and perform

        npm install 

### Flask
    To Prepare for flask make sure to set up a python virtual environment

    First go back to the root directory of the project

    create a python virtual environment if not already there:

        python -m venv .venv

    To activate, type:
    For Windows:

        .venv/Scripts/activate
    For Ubuntu/Mac:

        source .venv/bin/activate
    (Make sure scripts are allowed on the machine)

    One the virtual environment is activated install the required libraries by performing 

        pip install -r requirements.txt

## Setting up Google Cloud

    Go to https://console.cloud.google.com/welcome/ and click "Create or Select a Project". Then click on "New Project". Give your project a name and click create. Copy your project id.

    Create a .env file in codereview/api-server-flask/api/. Create a GCLOUD_PROJECT variable and set it to your project id.

    Go back to Google Cloud and go to APIs and Services -> Credentials. Make a new  OAuth 2.0 Client ID and set the application type to web application. Copy the client id and create a variable CLIENT_ID in .env and set it as the client id.

    Get your Application Default Credentials set up: https://cloud.google.com/docs/authentication/provide-credentials-adc 

    Place them in codereview/api-server-flask/api/credentials/googlecreds.json and create a variable in .env called GOOGLE_APPLICATION_CREDENTIALS whose value is credentials/googlecreds.json.

### Setting up Google OAuth 

    In order to utilize Google's OAuth services, you will need to obtain the credentials from your Google project.

    1. Go to your Google project page.
    2. On the left select API's and Services and then select the credentials sections.
    3. You will then create a new credential and select OAuth Client ID.
    4. Select Web Application for application type, and set a desired name.
    5. Add the URL's that will be allowed to connect to the services such as your localhost url, and your cloud deployment url.
    6. Replace the .flaskenv variables for client secret and id, and you should now be able to authenticate, login, and signup using Google OAuth.

### How to Setup Cloud SQL

    Go to Google Cloud -> SQL and click Create Instance. Select MySql. Give your instance a name and password. Save these.

    Go to codereview/api-server-flask/api/cloudSql.py

    Add INSTANCE_CONNECTION_NAME, DB_USER, DB_PASS, and DB_NAME variables to your .env file. Instance connection name has the format (YourProjectID):(YourRegion):(YourDatabaseName). DB_USER will be 'root' unless you made a new user.

    To work with cloud sql locally, you will need to use cloud-sql-proxy to connect to the cloud sql db from a local port.

    follow the tutorial provided by Google: https://cloud.google.com/sql/docs/mysql/connect-auth-proxy

    Download the cloud sql proxy file given and place it in a folder you can access in terminal later.

    To run the program, you will type:

        .\cloud-sql-proxy.exe --address 0.0.0.0 --port 5000 (YourProjectID):(YourRegion):(YourDatabaseName)

    Now, you can communicated with cloud sql from your port 5000 which is the port our Backend API runs.

### Setting up Google Gemini

    Follow instructions at this link https://cloud.google.com/vertex-ai/docs/start/cloud-environment

### How to Setup Google Buckets
    Go to https://console.cloud.google.com/storage/ and select your project for the app. Click on create bucket.

    Give your bucket a name and click create. Add the BUCKET_NAME variable in .env as your bucket's name.

    Your final .env file should look something like this

        CLIENT_ID = "some long string of numbers.apps.googleusercontent.com"
        
        GCLOUD_PROJECT = "(YourProjectID)"
        
        GOOGLE_APPLICATION_CREDENTIALS = "credentials/googlecreds.json"
        
        INSTANCE_CONNECTION_NAME = "(YourProjectID):(YourRegion):(YourDatabaseName)"
        
        BUCKET_NAME = '(YourBucketName)'
        
        DB_USER = "root"
        
        DB_PASS = "(YourDBPassword)"
        
        DB_NAME = "(YourDBName)"

## Setting up Github Oath App

    Create a Github Oauth app https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app

    You do not have a Homepage URL or Authorization callback URL right now, so wait until later.

    Create a github_oath_credentials.json, a json file of format 

        {
            "client-id": (Your Oauth App's client-id),
            "client-secret":  (Your Oath App's client-secret)
        }
        
    and place it in api-server-flask/api/credentials.

In codereview/react/src/components/GitHub/GitHubStatus.js, set the variable GitHub_Client_ID to your client-id

## Building Docker Containers and Deploying to Google Cloud
    Go here to install docker for your machine: https://docs.docker.com/engine/install/

    Go here to download Google Cloud: https://cloud.google.com/sdk/docs/install

### Creating Google Cloud Services
    Go to Google Cloud Run and open the 3 bar on the left. Click on Cloud Run. If it’s not there click on view all products to locate it.

    Click “create service” (unless you want to replace one of your current ones)

    For now, just set the container url to a dummy url.

    Give your service a name. You will need 2 services, one for your backend and one for your frontend, so make the name distinguishable.

    Pick a region close to where your website will likely be used.

    Click create.

    Repeat for the other service.

    Set your Github Oath App's homepage url and callback url to the url of the frontend service.

### Routing Container traffic
    In react/nginx/nginx.default.conf, change the proxy_pass value in location /api to the url of the backend will be run on. If it is on Google Cloud this will be the url of the backend service.

### Building Docker Containers
    perform

        docker compose build

    to build the docker containers.

### Deploying the Containers to Google Cloud

    Open your terminal and type 
        
        gcloud init

    Log in to your Google account.

    Then type in

        gcloud config set project (Your Project ID Here)

    Then configure docker with 

        gcloud auth configure-docker

    Run the following commands

        docker tag backend gcr.io/(Your Project ID Here)/backend

        docker push gcr.io/(Your Project ID Here)/backend

    Go to your backend service on Google Cloud, and set the container image url to what you just pushed.

    Repeat with the frontend container and service, replacing "backend" with "frontend".
