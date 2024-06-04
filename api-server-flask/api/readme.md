## How to Setup Cloud SQL

Go to Google Cloud -> SQL and click Create Instance. Select MySql. Give your instance a name and password. Save these for later. 

To work with cloud sql locally, you will need to use cloud-sql-proxy to connect to the cloud sql db from a local port.

follow the tutorial provided by Google: https://cloud.google.com/sql/docs/mysql/connect-auth-proxy

Download the cloud sql proxy file given and place it in a folder you can access in terminal later.

Make sure you have Application Default Credentials set up so you can run the program: https://cloud.google.com/docs/authentication/provide-credentials-adc 

Place them in codereview/api-server-flask/api/credentials/googlecreds.json


To run the program, you will type:

.\cloud-sql-proxy.exe --address 0.0.0.0 --port 5000 (YourProjectID):(YourRegion):(YourDatabaseName)

Now, you can communicated with cloud sql from your port 5000 which is the port our Backend API runs.

## How to Setup Google Buckets
Go to https://console.cloud.google.com/storage/ and select your project for the app. Click on create bucket.

Give your bucket a name and click create. Change the BUCKET_NAME variable in codereview/api-server-flask/api/utils/bucket.py to your bucket's name.

## How to run the flask development server

