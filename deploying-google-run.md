# Setting up Deployment for Cloud Run
0. Make sure you have [Docker Desktop on Windows](https://www.docker.com/products/docker-desktop/) installed and running.
1. Download the [Google Cloud CLI installer](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe).
2. Launch the installer and follow the prompts.
3. Open the terminal when the download finishes and run the `gcloud init` command. You will be redirected to a web browser prompting you to sign in with your Google credentials. Afterwards, Google Cloud SDK will send you a request form. Press Allow.
4. Go back to the terminal and select the cloud project `codereview-413200`.
5. Run the `gcloud auth configure-docker` command.

# Uploading a Docker Image to Cloud Run
0. Go to the directory where you usually run the `docker compose build` command. Make sure that the Docker image is updated before you try to upload.
1. Run the `docker image ls` command to find the name of the Docker image file you want to upload.
2. Run the `docker image tag SOURCE_IMAGE gcr.io/codereview-413200/TARGET_IMAGE` command. `SOURCE_IMAGE` is the name of the Docker image file you want to upload. `TARGET_IMAGE` is the name it will appear under when you select a Container Image URL under `gcr.io/codereview-413200/TARGET_IMAGE` from the **CONTAINER REGISTRY** tab.
3. Run the `docker push gcr.io/codereview-413200/TARGET_IMAGE` command. It should be available on your Cloud Run Project when you try to [create a new service](https://console.cloud.google.com/run/create?hl=en&project=codereview-413200). Select **Deploy one revision from an existing container image**. For the Container image URL, press **SELECT** and go to the **CONTAINER REGISTRY** tab. Expand the node that you tagged as `gcr.io/codereview-413200/TARGET_IMAGE` and verify that you were able to upload the latest revision.
# Creating a Service
1. Go to the [Google Cloud Run Dashboard](https://console.cloud.google.com/run?hl=en&project=codereview-413200) and press **Create Service** from the top menu.
2. Select *Deploy one revision from an existing container image*. For the Container image URL, press **SELECT** and go to the **CONTAINER REGISTRY** tab. Expand the node that you want to create a service for and select the latest revision.
3. Change the **Service name** if needed (service names must be unique for the project). By default, the service name will be whatever the Docker image name was inside `docker-compose.yml`.
4. Change the **Region** to *us-west2* (Los Angeles, California, North America) for development. The region will determine where traffic is routed.
5. Change **Authentication** to *Allow unauthenticated invocations* for development. Once the website implementation has authentication, it may need to change to **Require authentication**.
6. Keep **CPU allocation and pricing** at *CPU is only allocated during request processing* to avoid charges when the service is inactive.
7. Change **Revision autoscaling** according to needs. As an arbitrary choice, I set `Minimum number of instances = 0` and `Maximum number of instances = 3`, but it can be left at the default `Minimum number of instances = 0` and `Maximum number of instances = 100`.
8. Keep *Ingress control* at the default value `All`. I haven't done much research into what this does.
9. Expand **Container(s), Volumes, Networking, and Security** and change *Container port* to `80` for the react front-end service and `5000` for the flask back-end service.

# Updating an Already Existing Service
1. Go to the [Google Cloud Run Dashboard](https://console.cloud.google.com/run?hl=en&project=codereview-413200) and double-click into the service you want to update.
2. Go to the **REVISIONS** tab from the top menu and press **EDIT & DEPLOY NEW REVISION**.
3. Everything else should already be configured from when you created the service. You can change the Docker image URL and select the latest revision.

# Deployment Failed - Potential Problems and Fixes
```console
Default STARTUP TCP probe failed 1 time consecutively for container "[<container_name>]" on port <port_number>. The instance was not started.
```
1. Check if the container port number from the Google Run service matches the port number from the Docker image.
2. Check the **LOGS** tab from the top menu. Most likely, the issue will be from an upstream error caused by an invalid `proxy_pass` inside the `nginx.default.conf` file.
```js
server {
    listen       80;
    server_name  localhost;

    root   /usr/share/nginx/html;
    index index.html;
    error_page   500 502 503 504  /50x.html;

    location / {
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache";
    }

    location /static {
        expires 1y;
        add_header Cache-Control "public";
    }

    location /api {
        proxy_pass http://api:5000; // change to the URL for the back-end service
    }
}

```