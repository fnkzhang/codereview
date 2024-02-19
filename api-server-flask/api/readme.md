### How to setup

To work with cloud sql locally, you will need to use cloud-sql-proxy to connect to the cloud sql db from a local port.

follow the tutorial provided by Google: https://cloud.google.com/sql/docs/mysql/connect-auth-proxy

Download the cloud sql proxy file given and place it in a folder you can access in terminal later.

Make sure you have Application Default Credentials set up so you can run the program: https://cloud.google.com/docs/authentication/provide-credentials-adc 


To run the program, you will type 

.\cloud-sql-proxy.exe --address 0.0.0.0 --port 5000 codereview-413200:us-central1:cr-cloudsql-db

Now, you can communicated with cloud sql from your port 5000 which is the port our Backend API runs.