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

Find all instances of os.environ["GCLOUD_PROJECT"] = "codereview-413200" and change it to your project id. These are located in codereview/api-server-flask/api/utils/buckets.py and codereview/api-server-flask/api/cloudSql.py

Make sure you have Application Default Credentials set up so you can run the program: https://cloud.google.com/docs/authentication/provide-credentials-adc 

Place them in codereview/api-server-flask/api/credentials/googlecreds.json

### How to Setup Cloud SQL

Go to Google Cloud -> SQL and click Create Instance. Select MySql. Give your instance a name and password. Save these.

Go to codereview/api-server-flask/api/cloudSql.py

Change the instance_connection_name, db_user, db_pass, and db_name to your values. Instance connection name has the format (YourProjectID):(YourRegion):(YourDatabaseName).

To work with cloud sql locally, you will need to use cloud-sql-proxy to connect to the cloud sql db from a local port.

follow the tutorial provided by Google: https://cloud.google.com/sql/docs/mysql/connect-auth-proxy

Download the cloud sql proxy file given and place it in a folder you can access in terminal later.

To run the program, you will type:

.\cloud-sql-proxy.exe --address 0.0.0.0 --port 5000 (YourProjectID):(YourRegion):(YourDatabaseName)

Now, you can communicated with cloud sql from your port 5000 which is the port our Backend API runs.

## How to Setup Google Buckets
Go to https://console.cloud.google.com/storage/ and select your project for the app. Click on create bucket.

Give your bucket a name and click create. Change the BUCKET_NAME variable in codereview/api-server-flask/api/utils/buckets.py to your bucket's name.

## Setting up Github Oath App

Create a Github Oauth app https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app

You do not have a Homepage URL or Authorization callback URL right now, so wait until later.

Create a github_oath_credentials.json, a json file of format {"client-id": (Your Oauth App's client-id), "client-secret":  (Your Oath App's client-secret)} and place it in api-server-flask/api/credentials.

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

Open your terminal and type “gcloud init”. Log in to your Google account.

Type in “gcloud config set project (Your Project ID Here)” to your terminal.

Configure docker with “gcloud auth configure-docker” 

Type “docker tag backend gcr.io/(Your Project ID Here)/backend” into the terminal.

Type “docker push gcr.io/(Your Project ID Here)/backend” into the terminal.

Go to your backend service on Google Cloud, and set the container image url to what you just pushed.

Repeat with the frontend container and service, replacing "backend" with "frontend".
