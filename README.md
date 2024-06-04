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

### Routing Container traffic
In react/nginx/nginx.default.conf, change the proxy_pass value in location /api to the url of the backend will be run on. If it is on Google Cloud this will be the url of the backend service.

### Building Docker Containers
perform

docker compose build

to build the docker containers.

### Deploying the Containers to Google Cloud
Go to https://console.cloud.google.com/welcome/ and click "Create or Select a Project". Then click on "New Project". Give your project a name and click create. Copy your project id.

Open your terminal and type “gcloud init”. Log in to your Google account.

Type in “gcloud config set project (Your Project ID Here)” to your terminal.

Configure docker with “gcloud auth configure-docker” 

Type “docker tag backend gcr.io/(Your Project ID Here)/backend” into the terminal.

Type “docker push gcr.io/(Your Project ID Here)/backend” into the terminal.

Go to your backend service on Google Cloud, and set the container image url to what you just pushed.

Repeat with the frontend container and service, replacing "backend" with "frontend".
