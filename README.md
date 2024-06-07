## Initialization
### React
With Node.js installed, move to the react directory folder and perform

npm install 



### Flask
To Prepare for flask make sure to set up a python virtual environment

First go back to the root directory of the project

create a python virtual environment if not already there:

python -m venv .venv

To activate, type:

    .venv/Scripts/activate
(Make sure scripts are allowed on the machine)

One the virtual environment is activated install the required libraries by performing 

pip install -r requirements.txt


### Google OAuth Credentials

In order to utilize Google's OAuth services, you will need to obtain the credentials from your Google project.

1. Go to your Google project page.
2. On the left select API's and Services and then select the credentials sections.
3. You will then create a new credential and select OAuth Client ID.
4. Make sure to select Web Application for application type, and set a desired name.
5. Then you will want to add the URL's that will be allowed to connect to the services such as your localhost url, and your cloud deployment url.
6. Replacing the .flaskenv variables for client secret and id, you will now be able to authenticate, login, and signup using Google OAuth.
